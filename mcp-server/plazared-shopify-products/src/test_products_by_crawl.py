import asyncio
from products_by_crawl import search_products, get_product_details

async def test_search_products():
    print("\n测试搜索产品功能:")
    
    # 测试1: 按类别搜索
    print("\n1. 搜索 Solar Generator 类别的产品:")
    results = await search_products(category="Solar Generator")
    print(f"找到 {len(results)} 个产品")
    for product in results[:2]:  # 只显示前2个结果
        print(f"- {product['name']}")
    
    # 测试2: 按场景搜索
    print("\n2. 搜索适用于 camping 场景的产品:")
    results = await search_products(scenario="camping")
    print(f"找到 {len(results)} 个产品")
    for product in results[:2]:
        print(f"- {product['name']}")
    
    # 测试3: 组合搜索
    print("\n3. 搜索价格在 $100-$1000 之间的 Battery Pack:")
    results = await search_products(
        min_price=100,
        max_price=1000,
        category="Battery Pack"
    )
    print(f"找到 {len(results)} 个产品")
    for product in results[:2]:
        print(f"- {product['name']}")

async def test_get_product_details():
    print("\n测试获取产品详情功能:")
    
    # 获取一个已知存在的产品URL
    search_results = await search_products(category="Solar Generator")
    if search_results:
        test_url = search_results[0]['url']
        print(f"\n获取产品详情 URL: {test_url}")
        details = await get_product_details(test_url)
        print("产品详情:")
        print(f"- 名称: {details['name']}")
        print(f"- Meta标题: {details['meta_title']}")
        print(f"- Meta描述: {details['meta_description'][:100]}...")
    else:
        print("未找到测试产品")

async def main():
    print("开始测试 products_by_crawl.py 的功能...")
    
    await test_search_products()
    await test_get_product_details()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
