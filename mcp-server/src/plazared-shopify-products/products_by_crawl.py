from typing import Any, Dict, List, Tuple
from mcp.server.fastmcp import FastMCP
import asyncio
from firecrawl import FirecrawlApp, ScrapeOptions

# 初始化 FastMCP 服务器
mcp = FastMCP("jackery-products")

# 常量
BASE_URL = "https://www.jackery.com"
PRODUCT_LIST_URL = f"{BASE_URL}/collections/solar-generator"

# 初始化 FirecrawlApp
app = FirecrawlApp(api_key="fc-10aca4f473cc46a5bac7377c7a7f914a")

async def parse_product_details(crawl_result: Dict) -> Dict[str, Any]:
    """解析商品详细信息"""
    product = {
        "url": crawl_result.get("url", ""),
        "title": "",
        "price": "",
        "description": "",
        "specifications": [],
        "images": []
    }
    
    # 从爬取结果中提取数据
    html_content = crawl_result.get("content", {}).get("html", "")
    if html_content:
        # 使用 BeautifulSoup 解析 HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 获取标题
        title = soup.select_one('h1.product-title')
        if title:
            product["title"] = title.text.strip()
        
        # 获取价格
        price = soup.select_one('span.price')
        if price:
            product["price"] = price.text.strip()
        
        # 获取描述
        desc = soup.select_one('div.product-description')
        if desc:
            product["description"] = desc.text.strip()
        
        # 获取规格信息
        specs = []
        specs_container = soup.select('div.product-specifications div.specification-item')
        for spec_item in specs_container:
            spec_title = spec_item.select_one('div.specification-title')
            spec_value = spec_item.select_one('div.specification-value')
            if spec_title and spec_value:
                specs.append({
                    "title": spec_title.text.strip(),
                    "value": spec_value.text.strip()
                })
        product["specifications"] = specs
        
        # 获取图片
        images = soup.select('div.product-images img')
        product["images"] = [img.get('src') for img in images if img.get('src')]
    
    return product

async def get_product_urls() -> List[Tuple[str, str]]:
    """获取所有商品的型号名称和URL
    
    Returns:
        包含(型号名称, URL)元组的列表
    """
    # 使用 FirecrawlApp 爬取产品列表页
    crawl_result = await app.crawl_url(
        PRODUCT_LIST_URL,
        scrape_options=ScrapeOptions(
            formats=['html'],
            wait_for_selector='div.grid-product__content'
        )
    )
    
    products = []
    
    # 从爬取结果中提取数据
    html_content = crawl_result.get("content", {}).get("html", "")
    if html_content:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有商品链接和型号名称
        product_items = soup.select('div.grid-product__content')
        for item in product_items:
            link = item.select_one('a.grid-product__link')
            title = item.select_one('div.grid-product__title')
            
            if link and title:
                url = link.get('href')
                if url:
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
    
    # 并发获取商品详情
    async def fetch_product(model_name: str, url: str):
        crawl_result = await app.crawl_url(
            url,
            scrape_options=ScrapeOptions(
                formats=['html'],
                wait_for_selector='h1.product-title'
            )
        )
        
        product = await parse_product_details(crawl_result)
        if product:
            product['model_name'] = model_name
            products.append(product)
    
    # 使用 asyncio.gather 并发处理
    tasks = [fetch_product(model_name, url) for model_name, url in product_urls]
    await asyncio.gather(*tasks)
    
    return products

@mcp.tool()
async def get_product_by_url(url: str) -> Dict[str, Any]:
    """获取指定 URL 的商品信息
    
    Args:
        url: 商品页面的 URL
        
    Returns:
        包含商品详细信息的字典
    """
    crawl_result = await app.crawl_url(
        url,
        scrape_options=ScrapeOptions(
            formats=['html'],
            wait_for_selector='h1.product-title'
        )
    )
    
    return await parse_product_details(crawl_result)

if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')
