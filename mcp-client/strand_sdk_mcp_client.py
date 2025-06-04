from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

#command="uvx", args=["awslabs.aws-documentation-mcp-server@latest","../weather/weather.py"]
aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python", args=["/Users/yexw/PycharmProjects/mcp/mcp-server/src/plazared-weather/weather.py"]
        )
    )
)

with aws_docs_client:
    agent = Agent(tools=aws_docs_client.list_tools_sync())
    response = agent("Tell me about weather for Latitude 38.8951, Longitude -77.0364, use Chiense")
