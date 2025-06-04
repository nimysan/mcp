#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import os
import logging
from contextlib import AsyncExitStack
import boto3
from mcp import ClientSession, StdioServerParameters, stdio_client
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment variables from .env file
load_dotenv()

class MCPClient:
    def __init__(self, command):
        self.command = command
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.aclose()

    async def connect_to_server(self):
        server_script_path = self.command

        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        server_info = await self.session.initialize()
        logger.info("Connected to MCP server")
        return server_info

    async def get_available_tools(self):
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Retrieved {len(tools)} tools from MCP server")

        tool_specs = []
        for tool in tools:
            tool_specs.append({
                'toolSpec': {
                    'name': tool.name,
                    'description': tool.description or "No Description",
                    "inputSchema": {
                        "json": json.loads(tool.inputSchema) if isinstance(tool.inputSchema, str) else tool.inputSchema
                    }
                }
            })

        return tool_specs
    
    async def invoke_tool(self, tool_name, parameters, tool_use_id):
        logger.info(f"Invoking tool {tool_name} with parameters: {parameters}")
        response = await self.session.call_tool(tool_name, parameters)
        # print("-----")
        # print(response)
        # print("-------")
        
        # Format the response for Bedrock's toolResult format
        # print(f" typeof ----- " + response.content[0].text)
        tool_result = {
            "toolUseId": tool_use_id,
            "content": [{"json": {
                "text":response.content[0].text
            }}]
        }
        
        # Handle errors if present
        if response.isError:
            tool_result = {
                "toolUseId": tool_use_id,
                "content": [{"text": response.isError}],
                "status": "error"
            }
            
        return tool_result
    
async def generate_conversation(bedrock_client,
                        model_id,
                        system_prompts,
                        messages,
                        tool_config):
    """
    Sends messages to a model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The model ID to use.
        system_prompts (JSON) : The system prompts for the model to use.
        messages (JSON) : The messages to send to the model.

    Returns:
        response (JSON): The conversation that the model generated.

    """

    logger.info("Generating message with model %s", model_id)

    # Inference parameters to use.
    temperature = 0.5
    top_k = 200

    # Base inference parameters to use.
    inference_config = {"temperature": temperature}
    # Additional inference parameters to use.
    additional_model_fields = {"top_k": top_k}

    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        toolConfig=tool_config,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )

    # Log token usage.
    token_usage = response['usage']
    logger.info("Input tokens: %s", token_usage['inputTokens'])
    logger.info("Output tokens: %s", token_usage['outputTokens'])
    logger.info("Total tokens: %s", token_usage['totalTokens'])
    logger.info("Stop reason: %s", response['stopReason'])
    logger.info(json.dumps(response, indent=2))
    return response

async def generate_text(bedrock_client, model_id, tool_config, input_text, mcp_client):
    """Generates text using the supplied Amazon Bedrock model. If necessary,
    the function handles tool use requests and sends the result to the model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The Amazon Bedrock model ID.
        tool_config (dict): The tool configuration.
        input_text (str): The input text.
        mcp_client: The MCP client for tool invocation.
    Returns:
        The final conversation messages.
    """

    logger.info(f"Generating text with model {model_id}")

    # Inference parameters to use.
    temperature = 0.5
    top_k = 200

    # Base inference parameters to use.
    inference_config = {"temperature": temperature}
    # Additional inference parameters to use.
    additional_model_fields = {"top_k": top_k}

    # Create the initial message from the user input
    messages = [{
        "role": "user",
        "content": [{"text": input_text}]
    }]

    # System prompt
    system_prompts = [{"text": "You are a helpful assistant with access to tools. Use them when appropriate."}]
    logger.info(tool_config)
    response = await generate_conversation(bedrock_client, model_id, system_prompts, messages, tool_config)
    # Parse response
    output_message = response['output']['message']
    messages.append(output_message)
    stop_reason = response['stopReason']
    # logger.info("----stop reason-----"+stop_reason)
    if stop_reason == 'tool_use':
        # Tool use requested. Call the tool and send the result to the model.
        tool_requests = response['output']['message']['content']
        for tool_request in tool_requests:
            if 'toolUse' in tool_request:
                tool = tool_request['toolUse']
                # print(tool)
                logger.info("Requesting tool %s. Request: %s",
                            tool['name'], tool['toolUseId'])

                if tool['name'] == 'get_forecast':
                    tool_result = {}
                    try:
                        tool_result = await mcp_client.invoke_tool(tool['name'],tool['input'],tool['toolUseId'])
                    except Exception as err:
                        tool_result = {
                            "toolUseId": tool['toolUseId'],
                            "content": [{"text":  err.args[0]}],
                            "status": 'error'
                        }

                    tool_result_message = {
                        "role": "user",
                        "content": [
                            {
                                "toolResult": tool_result

                            }
                        ]
                    }
                    messages.append(tool_result_message)
                    # print("messages" + json.dumps(messages, indent=4))
                    # print("message before send to model")
                    # Send the tool result to the model.
                    response = bedrock_client.converse(
                        modelId=model_id,
                        messages=messages,
                        toolConfig=tool_config
                    )
                    output_message = response['output']['message']
                    # print(response)
                    # if response['stopReason'] == 'end_turn':
                    #     # Exit the agent loop when stop_reason is 'end_turn'
                    #     logger.info("Exiting agent loop due to 'end_turn' stop reason")
                    #     return messages

    # print the final response from the model.
    for content in output_message['content']:
        print(json.dumps(content, indent=4))

    # return messages

async def main():
    try:
        # Get MCP server path
        # mcp_server_path = input("Enter the path to your MCP server script: ")
        mcp_server_path = "/Users/yexw/PycharmProjects/awsgists/mcp/weather/weather.py"
        print(f"Using default MCP server path: {mcp_server_path}")
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Get model ID from environment or use default
        model_id = os.getenv('BEDROCK_MODEL_ID', '/anthropic.claude-3-5-sonnet-20241022-v2:0:200k')
        
        # Connect to MCP server and get available tools
        async with MCPClient(mcp_server_path) as mcp_client:
            server_info = await mcp_client.connect_to_server()
            tools = await mcp_client.get_available_tools()
            
            print(f"Connected to MCP server")
            print(f"Available tools: {json.dumps([t['toolSpec']['name'] for t in tools], indent=2)}")
            
            # Prepare tool config
            tool_config = {
                "tools": tools
            }
            
            # Start conversation loop
            conversation = []
            print("\nStarting conversation (type 'exit' to quit):")
            
            while True:
                # user_input = input("\nYou: ")
                # if user_input.lower() == 'exit':
                #     break
                    
                print("\nAssistant:")
                conversation = await generate_text(
                    bedrock_client, 
                    model_id, 
                    tool_config, 
                    "weather for Latitude 38.8951, Longitude -77.0364 ", 
                    mcp_client
                )
                
                # Break the loop if conversation is None or empty (happens when stop_reason is 'end_turn')
                if not conversation:
                    print("Conversation ended due to 'end_turn' stop reason, Valid values is :end_turn | tool_use | max_tokens | stop_sequence | guardrail_intervened | content_filtered ")
                    break

    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error(f"A client error occurred: {message}")
        print(f"A client error occurred: {message}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")
    else:
        print(f"Finished conversation with model {model_id}.")

if __name__ == "__main__":
    asyncio.run(main())
