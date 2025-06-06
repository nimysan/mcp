from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

import logging

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# 创建天气服务的 MCP 客户端
products_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python", 
            args=["/Users/yexw/PycharmProjects/mcp/mcp-server/src/plazared-shopify-products/products_by_crawl.py"]
        )
    )
)

# 通过firecrawl来获取
products_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="npx", 
            args=["/Users/yexw/PycharmProjects/mcp/mcp-server/src/plazared-shopify-products/products_by_crawl.py"]
        )
    )
)

# 这里可以添加其他 MCP 客户端
# 例如文档服务的 MCP 客户端
time_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["mcp-server-time","--local-timezone=America/New_York"]
        )
    )
)

def main():
    try:
        # 使用 with 语句同时管理多个客户端
        with products_client, time_client:
            # 合并所有客户端的工具
            all_tools = (
                products_client.list_tools_sync() +
                time_client.list_tools_sync()
            )
            
            # 创建具有所有工具的 Agent
            agent = Agent(tools=all_tools)
            
            # 使用 Agent 执行任务
            result = agent("Solor Generate 5000这个产品怎么样?")
            print("Agent 响应:", result)
            
            # Access metrics through the AgentResult
            print(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}")
            print(f"Execution time: {sum(result.metrics.cycle_durations):.2f} seconds")
            print(f"Tools used: {list(result.metrics.tool_metrics.keys())}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
