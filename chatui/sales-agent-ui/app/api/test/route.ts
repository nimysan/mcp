
import { createDataStreamResponse } from 'ai'

export async function POST() {
  // 模拟的对话流程
  const mockFlow = [
    {
      type: 'text',
      content: "你好! 我是一个销售助手。"
    },
    {
      type: 'text',
      content: "我们有一些很棒的产品推荐给你："
    },
    {
      type: 'products',
      products: [
        {
          url: "https://www.jackery.com/products/jackery-solar-generator-5000-plus",
          isRecommended: true
        },
        {
          url: "https://www.jackery.com/products/solar-generator-2000-plus?variant=41555999817815",
          isRecommended: false
        },
        {
          url: "https://www.jackery.com/products/jackery-explorer-1000-v2?variant=41738382245975",
          isRecommended: true
        }
      ]
    },
    {
      type: 'text',
      content: "这些是我们最受欢迎的产品，你对哪个感兴趣？"
    }
  ]

  // 创建数据流响应
  return createDataStreamResponse({
    // 设置响应状态和头部
    status: 200,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
    // 执行流式响应
    execute: async (writer) => {
      // 模拟延迟发送每条消息
      for (const item of mockFlow) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        if (item.type === 'text') {
          // 发送文本消息
          writer.write(`0:{"id":"mock","role":"assistant","content":"${item.content}","createdAt":${Date.now()}}\n`)
        } else if (item.type === 'products') {
          // 发送产品数据，使用 writeData 方法
          writer.writeData(JSON.parse(JSON.stringify({
            type: 'product-grid',
            products: item.products
          })))
        }
      }
    }
  })
}
