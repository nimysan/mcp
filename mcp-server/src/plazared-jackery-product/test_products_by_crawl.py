import asyncio
from products_by_crawl import get_product_urls, parse_product_details, BASE_URL, PRODUCT_LIST_URL

async def test_get_product_urls():
    """测试获取商品型号名称和URL的功能"""
    print("\n测试获取太阳能发电机产品列表...")
    print(f"从页面获取数据: {PRODUCT_LIST_URL}")
    
    products = await get_product_urls()
    
    # 验证返回结果不为空
    if len(products) == 0:
        raise AssertionError("未找到任何商品")
    
    # 验证每个商品都有型号名称和URL
    print("\n找到的产品:")
    for model_name, url in products:
        print(f"\n型号: {model_name}")
        print(f"URL: {url}")
        print("-" * 50)
        
        if not model_name:
            raise AssertionError("型号名称不能为空")
        if not url.startswith(BASE_URL):
            raise AssertionError(f"无效的URL: {url}")
    
    print(f"\n成功获取到 {len(products)} 个太阳能发电机产品")
    return products

async def test_parse_product_details():
    """测试解析商品详情的功能"""
    print("\n测试解析商品详情...")
    # 获取一个商品URL进行测试
    products = await get_product_urls()
    if not products:
        raise AssertionError("无法获取商品URL进行测试")
    
    # 测试第一个商品
    model_name, url = products[0]
    print(f"\n获取商品详情 - 型号: {model_name}")
    print(f"URL: {url}")
    
    product = await parse_product_details(url)
    
    # 验证返回的商品信息
    if not product:
        raise AssertionError("未能获取商品详情")
    if product['url'] != url:
        raise AssertionError("URL不匹配")
    if not product['title']:
        raise AssertionError("标题不能为空")
    
    print("\n商品详情:")
    print(f"标题: {product['title']}")
    print(f"价格: {product['price']}")
    print(f"描述长度: {len(product['description'])} 字符")
    print(f"规格数量: {len(product['specifications'])}")
    print(f"图片数量: {len(product['images'])}")

async def run_tests():
    """运行所有测试"""
    try:
        await test_get_product_urls()
        await test_parse_product_details()
        print("\n✅ 所有测试通过!")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {str(e)}")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_tests())
