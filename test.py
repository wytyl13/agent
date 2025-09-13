from pathlib import Path
import asyncio


from .tool.function_call import FunctionCall
from .tool.client_service import ClientService
from .tool.enhance_retrieval import EnhanceRetrieval
from .llm_api.ollama_llm import OllamaLLM
from .config.llm_config import LLMConfig
from .tool.order import Order
from .tool.role import Role


async def main():
    result = None
    history_message = None
    async for chunk, message in planning_agent.execute(
        question="确认",
        chat_history=[
            {"role": "user", "content": "我要新增一个角色"},
            {"role": "assistant", "content": "请提供具体的角色名称！"},
            {"role": "user", "content": "产品经理"},
            {"role": "assistant", "content": "请提供具体的权限！您可以从如下权限中选择：['服务项目管理', '商品分类管理', '设备类别管理']"},
            {"role": "user", "content": "服务项目和商品分类"},
            {"role": "assistant", "content": "<text_value>好的，收到新增：产品经理 * ['服务项目管理', '商品分类管理']。</text_value><confirm>请确认是否操作新增？</confirm>"},
        ]
        
        
        
        # chat_history=[
        #     {"role": "user", "content": "帮我预定1份鸡蛋"},
        #     {"role": "assistant", "content": "好的，收到订单：鸡蛋 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
        #     {"role": "user", "content": "确认"},
        #     {"role": "assistant", "content": "好的，已经帮您预定鸡蛋 * 1"},
        #     {"role": "user", "content": "帮我预定1杯牛奶"},
        #     {"role": "assistant", "content": "好的，收到订单：牛奶 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
        #     {"role": "user", "content": "取消"},
        #     {"role": "assistant", "content": "好的，没有为您下订单。如果您改变主意，请告诉我。"},
        # ]

    ):
        result = chunk
        message = message
    print(result, message)


def order(product_name: str, product_number: int, is_ensure: bool = False):
    if is_ensure:
        print(f"好的，已经帮您预定{product_name} * {product_number}")
    else:
        print(f"<text_value>好的，收到订单：{product_name} * {product_number}。</text_value><confirm>请确认是否下单？</confirm>")
    



if __name__ == '__main__':
    QWEN_OLLAMA_CONFIG_PATH = "/work/ai/agent/config/yaml/ollama_config_qwen.yaml"
    llm_qwen = OllamaLLM(config=LLMConfig.from_file(Path(QWEN_OLLAMA_CONFIG_PATH)))
    DEFAULT_RETRIEVAL_DATA_PATH = "/work/ai/agent/retrieval_data"
    DEFAULT_RETRIEVAL_STORAGE_PATH = "/work/ai/agent/retrieval_storage"
    enhance_qwen_admin = EnhanceRetrieval(
        llm=llm_qwen, 
        retrieval_flag=False, 
        data_dir=DEFAULT_RETRIEVAL_DATA_PATH, 
        index_dir=DEFAULT_RETRIEVAL_STORAGE_PATH,
        embedding_model_path="/work/ai/agent/models"
    )


    client_service = ClientService()
    order = Order()
    role = Role()
    planning_agent = FunctionCall(
        tools = [client_service, order, role],
        enhance_llm=enhance_qwen_admin,
    )
    asyncio.run(main())
    