import asyncio
from products_by_crawl import get_product_by_url, get_all_products

async def test_get_product_by_url():
    """测试获取单个商品信息"""
    url = "https://www.jackery.com/products/solar-generator-2000-pro"
    product = await get_product_by_url(url)
    print("\n=== 单个商品测试 ===")
    print(f"标题: {product.get('title')}")
    print(f"价格: {product.get('price')}")
    print(f"图片数量: {len(product.get('images', []))}")
    print(f"规格数量: {len(product.get('specifications', []))}")

async def test_get_all_products():
    """测试获取所有商品信息"""
    products = await get_all_products()
    print("\n=== 所有商品测试 ===")
    print(f"总共获取到 {len(products)} 个商品")
    for product in products:
        print(f"\n商品: {product.get('model_name')}")
        print(f"标题: {product.get('title')}")
        print(f"价格: {product.get('price')}")
        print("-" * 50)

async def main():
    """运行所有测试"""
    try:
        await test_get_product_by_url()
        await test_get_all_products()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
