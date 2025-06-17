import React, { useState, useEffect } from 'react';
import Image from 'next/image';

interface ProductLinkProps {
  url: string;
  isRecommended?: boolean;
}

const RecommendedIcon = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className="absolute top-2 right-2 z-10"
  >
    <circle cx="12" cy="12" r="12" fill="#FFC107" />
    <path
      d="M12 4l2.4 5.4 5.6.8-4 4.1.9 5.7-4.9-2.8-4.9 2.8.9-5.7-4-4.1 5.6-.8z"
      fill="#FFE082"
      stroke="#FFA000"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

interface ProductInfo {
  title: string;
  image: string;
  price: string;
}

export const ProductLink: React.FC<ProductLinkProps> = ({ url, isRecommended = false }) => {
  const [loading, setLoading] = useState(true);
  const [productInfo, setProductInfo] = useState<ProductInfo>({
    title: new URL(url).hostname.replace('www.', ''),
    image: "https://placehold.co/200x200",
    price: "$0.00"
  });

  useEffect(() => {
    const fetchProductInfo = async () => {
      try {
        const response = await fetch(url);
        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');

        // 尝试获取标题
        const title = 
          doc.querySelector('meta[property="og:title"]')?.getAttribute('content') ||
          doc.querySelector('meta[name="twitter:title"]')?.getAttribute('content') ||
          doc.title ||
          productInfo.title;

        // 尝试获取价格
        let price = 
          doc.querySelector('meta[property="product:price:amount"]')?.getAttribute('content') ||
          doc.querySelector('.price')?.textContent?.trim() ||
          doc.querySelector('[data-price]')?.getAttribute('data-price');

        // 处理价格格式
        if (price) {
          // 移除所有非数字和小数点的字符
          const numericPrice = price.replace(/[^\d.]/g, '');
          // 转换为数字并格式化为两位小数
          const formattedPrice = parseFloat(numericPrice);
          if (!isNaN(formattedPrice)) {
            price = `$${formattedPrice.toFixed(2)}`;
          } else {
            price = "$0.00";
          }
        } else {
          price = "$0.00";
        }

        // 尝试获取图片
        let image = 
          doc.querySelector('meta[property="og:image"]')?.getAttribute('content') ||
          doc.querySelector('meta[name="twitter:image"]')?.getAttribute('content') ||
          doc.querySelector('link[rel="icon"]')?.getAttribute('href');

        // 如果找到相对路径的图片，转换为绝对路径
        if (image && !image.startsWith('http')) {
          const baseUrl = new URL(url);
          image = new URL(image, baseUrl.origin).toString();
        }

        setProductInfo({
          title: title.trim(),
          image: image || productInfo.image,
          price: price
        });
      } catch (error) {
        console.error('Error fetching product info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProductInfo();
  }, [url]);

  return (
    <div className="relative flex flex-col gap-2 p-2 rounded-xl border border-gray-200 hover:border-gray-300 transition-colors bg-white shadow-sm h-full">
      {isRecommended && <RecommendedIcon />}
      
      {/* 商品图片 */}
      <div className="relative w-full pt-[100%]">
        <Image
          src={productInfo.image}
          alt={productInfo.title}
          fill
          className="object-contain rounded-lg"
        />
      </div>

      {/* 商品信息 */}
      <div className="flex flex-col flex-grow">
        <h3 className="text-base font-semibold line-clamp-2 mb-1">
          {loading ? "Loading..." : productInfo.title}
        </h3>
        
        {/* 价格信息 */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs text-gray-500">参考价格:</span>
          <span className="text-base font-medium text-gray-900">
            {productInfo.price}
          </span>
        </div>

        {/* More Detail 按钮 */}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto inline-flex justify-center items-center px-3 py-1.5 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors w-full"
        >
          More Detail
        </a>
      </div>
    </div>
  );
};
