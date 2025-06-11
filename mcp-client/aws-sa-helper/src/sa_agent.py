from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from strands.agent.conversation_manager import SlidingWindowConversationManager


import logging
from strands.models import BedrockModel

# Create a conversation manager with custom window size
# By default, SlidingWindowConversationManager is used even if not specified
conversation_manager = SlidingWindowConversationManager(
    window_size=20,  # Maximum number of message pairs to keep
)

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.DEBUG)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# Shopify products agents
products_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

# logging.info(products_client.list_tools_sync())

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

def convert_message(message):
    if isinstance(message, dict) and 'role' in message and 'content' in message:
        role = message['role']
        content = message['content']
        
        if isinstance(content, list) and len(content) > 0 and 'text' in content[0]:
            text = content[0]['text']
            return [role, text.strip()]
    
    return None
def convert_all_messages(messages):

    converted_messages = []

    for message in messages:

        converted = convert_message(message)

        if converted:

            converted_messages.append(converted)

    return converted_messages

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
            
            logging.debug(all_tools)
            # Create a Bedrock model instance
            bedrock_model = BedrockModel(
                model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                temperature=0.3,
                top_p=0.8,
            )
            # 创建具有所有工具的 Agent 
            agent = Agent(
                model=bedrock_model, 
                conversation_manager=conversation_manager, 
                tools=all_tools,
                system_prompt=(
                    """
                        你是一个AWS SA, 负责恢复客户关于AWS 服务的一些问题。 请严格按照AWS官方文档来回答问题。 回答问题的时候请遵照。内容/链接 这样的格式。
                    """
                ))
            
            # 使用 Agent 执行任务
            result = agent(message)
            
            return {
                "response": str(result),
                "messages": convert_all_messages(agent.messages),
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
    result = chat("RDS Proxy支持蓝绿部署吗？")
    print("Agent 响应:", result["response"])
    if "metrics" in result and result["metrics"]:
        print(f"Total tokens: {result['metrics']['total_tokens']}")
        print(f"Execution time: {result['metrics']['execution_time']:.2f} seconds")
        print(f"Tools used: {result['metrics']['tools_used']}")

if __name__ == "__main__":
    main()
