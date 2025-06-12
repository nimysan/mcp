import React from 'react';
import { ProductLink } from './product-link';

interface ProductLinkItem {
  url: string;
  isRecommended?: boolean;
}

interface ProductLinkGridProps {
  items: ProductLinkItem[];
}

export const ProductLinkGrid: React.FC<ProductLinkGridProps> = ({ items }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-2 gap-2">
      {items.map((item, index) => (
        <ProductLink
          key={`${item.url}-${index}`}
          url={item.url}
          isRecommended={item.isRecommended}
        />
      ))}
    </div>
  );
};
