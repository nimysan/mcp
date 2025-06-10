# MCP 多功能服务项目

这个项目是一个基于Model Context Protocol (MCP)的多功能服务集合，包含天气服务和Shopify商品管理服务。项目使用uv作为包管理工具。

## 项目结构

```
.
├── mcp-client/                          # MCP 客户端实现
│   ├── sample-agents/                   # 示例代理实现
│   │   ├── bedrock_mcp_client.py       # Amazon Bedrock Agent 集成
│   │   └── strand_sdk_mcp_client.py    # Strand Agent SDK 集成
│   ├── shopify-sales-agent/            # Shopify销售代理实现
│   │   ├── src/
│   │   │   ├── sales_agents.py         # 销售代理核心逻辑
│   │   │   └── producst_app_gradio.py  # Gradio界面实现
│   │   └── pyproject.toml              # 项目依赖配置
│   └── pyproject.toml                  # 客户端依赖配置
├── mcp-server/                         # MCP 服务器实现
│   ├── mcp-shopify-products/           # Shopify商品服务
│   │   ├── src/
│   │   │   └── products_repository/    # 商品仓库实现
│   │   └── pyproject.toml             # 项目依赖配置
│   ├── plazared-weather/              # 天气服务实现
│   │   ├── weather.py                 # 天气服务核心逻辑
│   │   └── pyproject.toml            # 项目依赖配置
│   └── pyproject.toml                 # 服务器依赖配置
```

## 功能特性

### 1. Shopify商品服务

- **商品管理功能**
  - 商品信息抓取和管理
  - 销售代理系统
  - Gradio交互界面

### 2. 天气服务

- **天气信息查询**
  - `get_alerts`: 获取指定美国州的天气预警信息
  - `get_forecast`: 获取指定经纬度位置的天气预报信息
  - 使用National Weather Service (NWS) API作为数据源

### MCP 客户端集成

提供多种集成方式：

1. **Amazon Bedrock Agent集成**
   - 使用Amazon Bedrock Runtime服务
   - 支持与Claude 3模型的对话
   - 实现完整的工具调用生命周期

2. **Strand Agent SDK集成**
   - 使用Strand Agent SDK进行简化集成
   - 提供简洁的API调用方式

3. **Shopify销售代理**
   - 基于Gradio的交互式界面
   - 智能销售代理功能

## 依赖要求

- Python >= 3.12
- 核心依赖：
  - mcp >= 1.9.2
  - anthropic >= 0.52.1
  - httpx >= 0.28.1
  - gradio (用于Shopify销售代理界面)
  - python-dotenv >= 1.1.0

## 安装说明

使用uv安装各个模块的依赖：

```bash
# 安装MCP客户端依赖
cd mcp-client
uv pip install -e .

# 安装Shopify销售代理依赖
cd shopify-sales-agent
uv pip install -e .

# 安装Shopify商品服务依赖
cd ../../mcp-server/mcp-shopify-products
uv pip install -e .

# 安装天气服务依赖
cd ../plazared-weather
uv pip install -e .
```

## 使用方法

### 启动Shopify销售代理

```bash
cd mcp-client/shopify-sales-agent/src
python producst_app_gradio.py
```

### 启动天气服务

```bash
cd mcp-server/plazared-weather
python weather.py
```

### 配置Bedrock Agent客户端

1. 设置环境变量：
   ```
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=/anthropic.claude-3-5-sonnet-20241022-v2:0:200k
   ```

2. 运行客户端：
   ```bash
   cd mcp-client/sample-agents
   python bedrock_mcp_client.py
   ```

## 技术说明

- 使用FastMCP框架实现MCP服务器
- 实现完整的错误处理和超时机制
- 支持标准的JSON响应格式
- 集成Gradio实现交互式界面

## 注意事项

- 确保正确配置AWS凭证以使用Bedrock服务
- 天气数据仅支持美国地区信息
- 所有API调用都有适当的超时处理机制
