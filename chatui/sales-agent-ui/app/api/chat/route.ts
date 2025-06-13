import { createDataStreamResponse } from 'ai'

export async function POST() {
  // 模拟的响应数据
  const mockResponses = [
    "你好!",
    "我是一个销售助手。",
    "我可以帮你了解我们的产品。",
    "有什么我可以帮你的吗?"
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
      for (const text of mockResponses) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 使用正确的数据流格式写入文本
        writer.write(`0:{"id":"mock","role":"assistant","content":"${text}","createdAt":${Date.now()}}\n`)
      }
    }
  })
}
