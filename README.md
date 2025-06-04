# MCP 天气服务示例项目

这个项目展示了如何使用 Model Context Protocol (MCP) 来构建和使用天气服务，同时演示了如何通过 Amazon Bedrock Agent 和 Strand Agent SDK 两种不同的方式来调用 MCP 客户端。项目使用 uv 作为包管理工具。

## 项目结构

```
.
├── mcp-client/                 # MCP 客户端实现
│   ├── bedrock_mcp_client.py  # Amazon Bedrock Agent 集成
│   ├── strand_sdk_mcp_client.py# Strand Agent SDK 集成
│   └── pyproject.toml         # 客户端依赖配置
├── mcp-server/                 # MCP 服务器实现
│   ├── src/
│   │   └── plazared-weather/  # 天气服务实现
│   │       ├── weather.py     # 天气服务核心逻辑
│   │       └── pyproject.toml # 天气服务依赖配置
│   └── pyproject.toml         # 服务器依赖配置
```

## 功能特性

### MCP 服务器 (Weather Service)

- 提供两个主要 API 端点：
  - `get_alerts`: 获取指定美国州的天气预警信息
  - `get_forecast`: 获取指定经纬度位置的天气预报信息
- 使用 National Weather Service (NWS) API 作为数据源
- 支持标准的 MCP 协议通信

### MCP 客户端

提供两种不同的集成方式：

1. **Amazon Bedrock Agent 集成** (bedrock_mcp_client.py)
   - 使用 Amazon Bedrock Runtime 服务
   - 支持与 Claude 3 模型的对话
   - 实现了完整的工具调用生命周期
   - 支持异步操作

2. **Strand Agent SDK 集成** (strand_sdk_mcp_client.py)
   - 使用 Strand Agent SDK 进行简化的集成
   - 提供更简洁的 API 调用方式
   - 支持同步操作

## 依赖要求

### MCP 客户端
- Python >= 3.12
- anthropic >= 0.52.1
- mcp >= 1.9.2
- python-dotenv >= 1.1.0

### 天气服务
- Python >= 3.12
- httpx >= 0.28.1
- mcp >= 1.9.2

## 安装说明

1. 克隆项目后，使用 uv 安装依赖：

```bash
# 安装 MCP 客户端依赖
cd mcp-client
uv pip install -e .

# 安装天气服务依赖
cd ../mcp-server/src/plazared-weather
uv pip install -e .
```

## 使用方法

### 启动天气服务

```bash
cd mcp-server/src/plazared-weather
python weather.py
```

### 使用 Bedrock Agent 客户端

1. 设置环境变量：
   - 创建 `.env` 文件并配置：
     ```
     AWS_REGION=us-east-1
     BEDROCK_MODEL_ID=/anthropic.claude-3-5-sonnet-20241022-v2:0:200k
     ```

2. 运行客户端：
```bash
cd mcp-client
python bedrock_mcp_client.py
```

### 使用 Strand Agent SDK 客户端

```bash
cd mcp-client
python strand_sdk_mcp_client.py
```

## 示例查询

1. 获取天气预报：
```python
# 使用经纬度获取天气预报
"Tell me about weather for Latitude 38.8951, Longitude -77.0364"
```

2. 获取天气预警：
```python
# 获取特定州的天气预警
"What are the current weather alerts for CA?"
```

## 技术说明

- 项目使用 FastMCP 框架实现 MCP 服务器
- 使用 httpx 进行异步 HTTP 请求
- 实现了完整的错误处理和超时机制
- 支持标准的 JSON 响应格式

## 注意事项

- 确保已正确配置 AWS 凭证以使用 Bedrock 服务
- 天气数据来自 National Weather Service API，仅支持美国地区的天气信息
- 所有 API 调用都有适当的超时处理机制
