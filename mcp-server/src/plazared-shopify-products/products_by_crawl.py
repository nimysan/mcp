from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
from decimal import Decimal
import re
import requests
import os
import json
from datetime import datetime, timedelta

# 初始化 FastMCP 服务器
mcp = FastMCP("jackery-products")

# 常量
PRODUCTS_CSV_PATH = "/Users/yexw/PycharmProjects/mcp/mcp-server/src/plazared-shopify-products/products.csv"

class ProductFilter:
    """产品过滤器类"""
    def __init__(self, 
                 min_price: Optional[float] = None,
                 max_price: Optional[float] = None,
                 category: Optional[str] = None,
                 scenario: Optional[str] = None):
        self.min_price = min_price
        self.max_price = max_price
        self.category = category
        self.scenario = scenario

    def match_price(self, description: str) -> bool:
        """检查价格是否在范围内"""
        if not (self.min_price or self.max_price):
            return True
            
        # 从描述中提取价格
        price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', str(description))
        if not price_match:
            return True
            
        try:
            price = Decimal(price_match.group(1).replace(',', ''))
            if self.min_price and price < self.min_price:
                return False
            if self.max_price and price > self.max_price:
                return False
            return True
        except:
            return True

    def match_category(self, name: str, description: str) -> bool:
        """检查产品类别是否匹配"""
        if not self.category:
            return True
            
        category_lower = self.category.lower()
        return (category_lower in str(name).lower() or 
                category_lower in str(description).lower())

    def match_scenario(self, description: str) -> bool:
        """检查使用场景是否匹配"""
        if not self.scenario:
            return True
            
        scenario_lower = self.scenario.lower()
        return scenario_lower in str(description).lower()

    def match_product(self, product: Dict[str, Any]) -> bool:
        """检查产品是否满足所有过滤条件"""
        return (self.match_price(product.get('Product Description', '')) and
                self.match_category(product.get('Name', ''), 
                                  product.get('Product Description', '')) and
                self.match_scenario(product.get('Product Description', '')))

def load_products() -> pd.DataFrame:
    """加载产品数据"""
    # 确保字符串列不会被转换为float
    return pd.read_csv(PRODUCTS_CSV_PATH, dtype={
        'Name': str,
        'URL': str,
        'Meta Title': str,
        'Meta Description': str,
        'Product Description': str
    })

@mcp.tool()
async def search_products(min_price: Optional[float] = None,
                        max_price: Optional[float] = None,
                        category: Optional[str] = None,
                        scenario: Optional[str] = None) -> List[Dict[str, Any]]:
    """搜索产品
    
    Args:
        min_price: 最低价格
        max_price: 最高价格
        category: 产品类别 (如 "Solar Generator", "Battery Pack" 等)
        scenario: 使用场景 (如 "camping", "home backup" 等)
    
    Returns:
        满足条件的产品列表
    """
    # 创建过滤器
    product_filter = ProductFilter(
        min_price=min_price,
        max_price=max_price,
        category=category,
        scenario=scenario
    )
    
    # 加载产品数据
    df = load_products()
    
    # 应用过滤器
    filtered_products = []
    for _, row in df.iterrows():
        product = row.to_dict()
        if product_filter.match_product(product):
            filtered_products.append({
                'name': str(product['Name']),
                'url': str(product['URL']),
                'description': str(product['Product Description'])
            })
    
    return filtered_products

def get_cache_path(url: str) -> str:
    """获取缓存文件路径"""
    # 将URL转换为文件名安全的格式
    cache_filename = re.sub(r'[^\w]', '_', url) + '.json'
    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, cache_filename)

def is_cache_valid(cache_path: str) -> bool:
    """检查缓存是否在TTL期限内"""
    if not os.path.exists(cache_path):
        return False
    
    # 检查文件修改时间是否在1分钟内
    mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
    return datetime.now() - mtime < timedelta(minutes=1)

@mcp.tool()
async def get_product_details(url: str) -> Dict[str, Any]:
    """获取指定URL的产品详情
    
    Args:
        url: 产品页面URL
    
    Returns:
        包含产品详细信息的字典
    """
    cache_path = get_cache_path(url)
    
    # 检查缓存是否有效
    if is_cache_valid(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        # 提取产品信息
        # 这里使用简单的数据结构存储,实际使用时可能需要更复杂的解析逻辑
        product_data = {
            'url': url,
            'html_content': html_content,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, ensure_ascii=False, indent=2)
        
        return product_data
        
    except Exception as e:
        return {"error": f"Failed to fetch product details: {str(e)}"}

if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')
