import { bedrock } from "@ai-sdk/amazon-bedrock";
import { streamText } from "ai";
import { z } from "zod";
import { crawlProductDetail } from "@/app/utils/productCrawler";

export const maxDuration = 30;

const system_prompt = "你是一个导购专家，永远用中文输出. ## 输出要求 1. 不要把内部工具显示出来 2. 尽量以一个专业导购的语言 3. 如果希望是做性价比对比， 通常是从价格/电容量/充电时长等角度 然后以Markdown输出";

import { experimental_createMCPClient, generateText } from 'ai';
import { Experimental_StdioMCPTransport } from 'ai/mcp-stdio';
// Initialize an MCP client to connect to a `stdio` MCP server:
const transport = new Experimental_StdioMCPTransport({
  command: 'uv',
  args: ["run","mcp-shopify-products"],
});

const clientOne = await experimental_createMCPClient({
  transport,
});

const toolSetOne = await clientOne.tools();
// console.log(toolSetOne)
console.log(generateText)

console.log(toolSetOne)
console.log("------------------")
const tools = toolSetOne;

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: bedrock("anthropic.claude-3-5-sonnet-20240620-v1:0"),
    messages,
    system: system_prompt,
    tools: tools,
    // tools: {
    //   listProductList: {
    //     description: "List product lists",
    //     parameters: z.object({
    //       query: z.string()
    //     }),
    //     execute: async ({ }) => {
    //       // Server-side database access
    //       const results = [
    //         { "url": "https://www.jackery.com/products/explorer-1500-portable-power-station-refurbished", "isRecommended": true },
    //         { "url": "https://www.jackery.com/products/jackery-solar-generator-2000-plus-kit-6kwh", "isRecommended": false }
    //       ]
    //       return {
    //         "results": results
    //       };
    //     }
    //   },
    //   getProductDetail: {
    //     description: "Get Product Detail(like specification, price, promotion)",
    //     parameters: z.object({
    //       product_url: z.string()
    //     }),
    //     execute: async ({ product_url }) => {
    //       try {
    //         const productDetail = await crawlProductDetail(product_url);
    //         return {
    //           results: productDetail
    //         };
    //       } catch (error) {
    //         console.error('Error getting product detail:', error);
    //         return {
    //           results: {
    //             price: 0,
    //             Currency: 'USD'
    //           }
    //         };
    //       }
    //     }
    //   }
    // },
  });
  return result.toDataStreamResponse();
}
