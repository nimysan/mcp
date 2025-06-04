from typing import Any, Dict, List, Tuple
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
import asyncio

# 初始化 FastMCP 服务器
mcp = FastMCP("jackery-products")

# 常量
BASE_URL = "https://www.jackery.com"
PRODUCT_LIST_URL = f"{BASE_URL}/collections/solar-generator"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

async def fetch_page(url: str) -> str:
    """获取页面内容"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取页面失败: {str(e)}")
            return ""

async def parse_product_details(url: str) -> Dict[str, Any]:
    """解析商品详细信息"""
    html = await fetch_page(url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 获取商品基本信息
    product = {
        "url": url,
        "title": "",
        "price": "",
        "description": "",
        "specifications": [],
        "images": []
    }
    
    # 获取标题
    title_elem = soup.find('h1', {'class': 'product-title'})
    if title_elem:
        product["title"] = title_elem.text.strip()
    
    # 获取价格
    price_elem = soup.find('span', {'class': 'price'})
    if price_elem:
        product["price"] = price_elem.text.strip()
    
    # 获取描述
    desc_elem = soup.find('div', {'class': 'product-description'})
    if desc_elem:
        product["description"] = desc_elem.text.strip()
    
    # 获取规格信息
    specs_container = soup.find('div', {'class': 'product-specifications'})
    if specs_container:
        specs = []
        for spec in specs_container.find_all('div', {'class': 'specification-item'}):
            spec_title = spec.find('div', {'class': 'specification-title'})
            spec_value = spec.find('div', {'class': 'specification-value'})
            if spec_title and spec_value:
                specs.append({
                    "title": spec_title.text.strip(),
                    "value": spec_value.text.strip()
                })
        product["specifications"] = specs
    
    # 获取图片
    image_container = soup.find('div', {'class': 'product-images'})
    if image_container:
        for img in image_container.find_all('img'):
            if 'src' in img.attrs:
                product["images"].append(img['src'])
    
    return product

async def get_product_urls() -> List[Tuple[str, str]]:
    """获取所有商品的型号名称和URL
    
    Returns:
        包含(型号名称, URL)元组的列表
    """
    html = await fetch_page(PRODUCT_LIST_URL)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # 查找所有商品链接和型号名称
    for product_item in soup.find_all('div', {'class': 'grid-product__content'}):
        link = product_item.find('a', {'class': 'grid-product__link'})
        title = product_item.find('div', {'class': 'grid-product__title'})
        
        if link and 'href' in link.attrs and title:
            url = link['href']
            if not url.startswith('http'):
                url = BASE_URL + url
            # 从标题中提取型号名称
            model_name = title.text.strip()
            if "Solar Generator" in model_name:
                model_name = model_name.replace("Solar Generator", "").strip()
            products.append((model_name, url))
    
    return products

@mcp.tool()
async def get_all_products() -> List[Dict[str, Any]]:
    """获取所有商品信息
    
    Returns:
        包含所有商品详细信息的列表
    """
    product_urls = await get_product_urls()
    products = []
    
    for model_name, url in product_urls:
        product = await parse_product_details(url)
        if product:
            product['model_name'] = model_name
            products.append(product)
    
    return products

@mcp.tool()
async def get_product_by_url(url: str) -> Dict[str, Any]:
    """获取指定 URL 的商品信息
    
    Args:
        url: 商品页面的 URL
        
    Returns:
        包含商品详细信息的字典
    """
    return await parse_product_details(url)

if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')
