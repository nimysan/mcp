# MCP Client with Amazon Bedrock

This project demonstrates how to use the Model Context Protocol (MCP) with Amazon Bedrock's Converse API.

## Prerequisites

- Python 3.12 or higher
- AWS credentials configured with access to Amazon Bedrock
- An MCP server implementation

## Installation

1. Set up a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create a `.env` file with your AWS configuration:
```
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

## Usage

Run the Bedrock MCP client:

```bash
python bedrock_mcp_client.py
```

When prompted, enter the path to your MCP server script. The client will:

1. Connect to the MCP server
2. Retrieve available tools
3. Start a conversation where you can interact with the model
4. The model will use MCP tools when appropriate

## How It Works

1. The client establishes a connection with the MCP server using stdio
2. It retrieves available tools from the server
3. When you send a message, it's forwarded to Amazon Bedrock's Converse API
4. If the model decides to use a tool, the client:
   - Extracts the tool call
   - Invokes the tool through the MCP server
   - Sends the tool response back to the model
   - Gets the final response

## Example MCP Server

You need to provide your own MCP server implementation. A simple example might look like:

```python
from mcp import Server, Tool, ToolCall, ToolResponse

class MyServer(Server):
    async def initialize(self):
        return {"name": "MyMCPServer", "version": "1.0.0"}

    async def list_tools(self):
        return [
            Tool(
                name="calculator",
                description="Performs basic arithmetic operations",
                inputSchema="""
                {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                }
                """
            )
        ]

    async def invoke_tool(self, call: ToolCall) -> ToolResponse:
        if call.name == "calculator":
            params = call.parameters
            operation = params["operation"]
            a = params["a"]
            b = params["b"]
            
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                result = a / b if b != 0 else "Error: Division by zero"
                
            return ToolResponse(result={"result": result})
        
        return ToolResponse(error="Unknown tool")

if __name__ == "__main__":
    server = MyServer()
    server.start()
```

Save this as `my_mcp_server.py` and use it with the client.
