import logging
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

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
            args=["run","hellojoke"]
        )
    )
)

print(products_client.list_tools_sync())