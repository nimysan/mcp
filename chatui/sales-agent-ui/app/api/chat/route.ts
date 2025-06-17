import { bedrock } from "@ai-sdk/amazon-bedrock";
import { streamText } from "ai";
import { z } from "zod";

export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: bedrock("anthropic.claude-3-5-sonnet-20240620-v1:0"),
    messages,
    system: "你是一个导购专家，永远用中文输出",
    tools: {
      listProductList: {
        description: "List product lists",
        parameters: z.object({
          query: z.string()
        }),
        execute: async ({ }) => {
          // Server-side database access
          const results = [
            { "url": "https://www.jackery.com/products/explorer-1500-portable-power-station-refurbished", "isRecommended": true },
            { "url": "https://www.jackery.com/products/jackery-solar-generator-2000-plus-kit-6kwh", "isRecommended": false }
          ]
          return {
            "results": results
          };
        }
      },
      getProductPrice: {
        description: "Get Product Price By Specific URL",
        parameters: z.object({
          product_url: z.string()
        }),
        execute: async ({ }) => {
          // Server-side database access
          const results = {
            "price": 224.34,
            "Currency": "USD"
          }
          return {
            "results": results
          };
        }
      }
    },
  });
  return result.toDataStreamResponse();
}

