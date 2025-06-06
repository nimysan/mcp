import asyncio
from crawl4ai import *
from crawl4ai.extraction_strategy import LLMExtractionStrategy


extraction_strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="openai/gpt-4", api_token="YOUR_OPENAI_KEY"),
    schema=MyModel.model_json_schema(),
    extraction_type="schema",
    instruction="Extract a list of items from the text with 'name' and 'price' fields.",
    chunk_token_threshold=1200,
    overlap_rate=0.1,
    apply_chunking=True,
    input_format="html",
    extra_args={"temperature": 0.1, "max_tokens": 1000},
    verbose=True
)


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.jackery.com/",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())