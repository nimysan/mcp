import React from 'react';
import { ProductLink } from './product-link';
import { makeAssistantToolUI } from "@assistant-ui/react";

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

interface ContentItem {
  type: string;
  text: string;
}

interface ContentObject {
  content: ContentItem[];
}


// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getJsonArray(obj: { content: { type: string; text: string }[] }): any[] {
  return obj.content
    .filter(item => item.type === 'text')
    .map(item => {
      try {
        return JSON.parse(item.text);
      } catch (e) {
        console.error('Failed to parse JSON:', e);
        return null;
      }
    })
    .filter(item => item !== null);
}

// 使用示例
const data: ContentObject = {
  content: [
    {
      type: "text",
      text: `{
 "name": "Solar Generator 2000 v2（100 Mini）",
 "url": "https://www.jackery.com/products/jackery-solar-generator-2000-v2-100-mini",
 "description": "2042Wh capacity and 2200W output, powering over 1 day of emergency"
}`
    }
  ]
};

const jsonArray = getJsonArray(data);
console.log(jsonArray);

export const SearchResultsUI = makeAssistantToolUI<{
  query: string;
}, { content: { type: string; text: string }[] }>({
  toolName: "search_products", // Must match the registered tool's name
  render: ({ args, result }) => {
    return (
      <div className="search-results">
        <h3>Search: {args.query}</h3>
        {(() => {
          if (!result) return <p>No results available</p>;
          const items = getJsonArray(result);
          return items.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {items.map((item, index) => (
                <ProductLink
                  key={`${item.url}-${index}`}
                  url={item.url}
                  isRecommended={false}
                />
              ))}
            </div>
          ) : (
            <p>No results found</p>
          );
        })()}
      </div>
    );
  }
});
