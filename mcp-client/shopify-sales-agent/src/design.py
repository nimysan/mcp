from strands import Agent
from strands_tools import swarm

# Create an agent with swarm capability
agent = Agent(tools=[swarm])

# Process a complex task with multiple agents in parallel
result = agent.tool.swarm(
    task="我有办法可以获取到所有Jackery shopify网站的信息，可以爬取所有产品数据，然后每个产品会有一个链接。 当给客户介绍具体产品的时候，我可以通过链接获取价格，variant,和优惠券等。请基于此信息设计一个导购AI Agent。给我MCP Tool的设计和Agent分布设计。并给我合适的提示词",
    swarm_size=4,
    coordination_pattern="collaborative"
)

# The result contains contributions from all swarm agents
print(result["content"])