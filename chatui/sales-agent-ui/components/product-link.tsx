import React, { useState, useEffect } from 'react';
import Image from 'next/image';

interface ProductLinkProps {
  url: string;
}

interface ProductInfo {
  title: string;
  image: string;
}

export const ProductLink: React.FC<ProductLinkProps> = ({ url }) => {
  const [loading, setLoading] = useState(true);
  const [productInfo, setProductInfo] = useState<ProductInfo>({
    title: new URL(url).hostname.replace('www.', ''),
    image: "https://placehold.co/200x200"
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
          image: image || productInfo.image
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
    <a 
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-start gap-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
    >
      {/* 左侧商品图片 */}
      <div className="relative w-[100px] h-[100px] flex-shrink-0">
        <Image
          src={productInfo.image}
          alt={productInfo.title}
          fill
          className="object-cover rounded-md"
        />
      </div>

      {/* 右侧元数据 */}
      <div className="flex flex-col gap-2">
        <h3 className="text-lg font-semibold">
          {loading ? "Loading..." : productInfo.title}
        </h3>
        <p className="text-sm text-gray-600 line-clamp-2">
          {url}
        </p>
      </div>
    </a>
  );
};
