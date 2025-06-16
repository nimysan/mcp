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


export const SearchResultsUI = makeAssistantToolUI<{
  query: string;
}, {
  results: Array<{
    url: string;
    isRecommended: boolean;
  }>;
}>({
  toolName: "listProductList", // Must match the registered tool's name
  render: ({ args, result }) => {
    return (
      <div className="search-results">
        <h3>Search: {args.query}</h3>
        {/* <h2>{JSON.stringify(result)}</h2> */}
        {result && result.results ? (
          result.results.map((item, index) => (
            <ProductLink
              key={`${item.url}-${index}`}
              url={item.url}
              isRecommended={item.isRecommended}
            />
          ))
        ) : (
          <p>No results found</p>
        )}
      </div>
    );
  }
});