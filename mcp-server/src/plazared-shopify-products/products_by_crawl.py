from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
from decimal import Decimal
import re

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

@mcp.tool()
async def get_product_details(url: str) -> Dict[str, Any]:
    """获取指定URL的产品详情
    
    Args:
        url: 产品页面URL
    
    Returns:
        包含产品详细信息的字典
    """
    # 加载产品数据
    df = load_products()
    
    # 查找匹配的产品
    matches = df[df['URL'] == url]
    if len(matches) == 0:
        return {"error": "Product not found"}
        
    product = matches.iloc[0].to_dict()
    return {
        'name': str(product['Name']),
        'url': str(product['URL']),
        'meta_title': str(product['Meta Title']),
        'meta_description': str(product['Meta Description']),
        'description': str(product['Product Description'])
    }

if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')
