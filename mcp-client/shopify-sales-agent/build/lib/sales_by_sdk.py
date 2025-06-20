from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from strands.agent.conversation_manager import SlidingWindowConversationManager

# Create a conversation manager with custom window size
# By default, SlidingWindowConversationManager is used even if not specified
conversation_manager = SlidingWindowConversationManager(
    window_size=10,  # Maximum number of message pairs to keep
)

import logging

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# Shopify products agents
products_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uv", 
            args=["run","product-mcp"]
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

def chat(message):
    """
    与Agent进行对话的方法
    
    Args:
        message (str): 用户输入的消息
        
    Returns:
        dict: 包含回复内容和指标的字典
    """
    try:
        with products_client, time_client:
            # 合并所有客户端的工具
            all_tools = (
                products_client.list_tools_sync() +
                time_client.list_tools_sync()
            )
            
            # 创建具有所有工具的 Agent
            agent = Agent(conversation_manager=conversation_manager, tools=all_tools)
            
            # 使用 Agent 执行任务
            result = agent(message)
            
            return {
                "response": str(result),
                "metrics": {
                    "total_tokens": result.metrics.accumulated_usage['totalTokens'],
                    "execution_time": sum(result.metrics.cycle_durations),
                    "tools_used": list(result.metrics.tool_metrics.keys())
                }
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "response": None,
            "metrics": None
        }

def main():
    # 测试chat方法
    result = chat("Solor Generate 5000这个产品怎么样?")
    print("Agent 响应:", result["response"])
    if "metrics" in result and result["metrics"]:
        print(f"Total tokens: {result['metrics']['total_tokens']}")
        print(f"Execution time: {result['metrics']['execution_time']:.2f} seconds")
        print(f"Tools used: {result['metrics']['tools_used']}")

if __name__ == "__main__":
    main()
