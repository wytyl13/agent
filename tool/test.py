from ..llm_api.ollama_llm import OllamaLLM
from ..config.llm_config import LLMConfig



ollama_llm = OllamaLLM(
    config=LLMConfig.from_file("/work/ai/agent/config/yaml/ollama_config_qwen.yaml")
)

async def main():
    async for chunk in ollama_llm._whoami_text_stream(
        messages=[{"role": "user", "content": "我是谁？"}],
        user_stop_words=[],
        timeout=10
    ):
        print(chunk)
        
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    