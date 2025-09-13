#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/26 15:45
@Author  : weiyutao
@File    : enhance_retrieval.py
"""
from typing import (
    Optional,
    Type,
    List,
    Dict,
    overload
)
from pydantic import BaseModel, Field
from .retrieval import Retrieval
from datetime import datetime
from pathlib import Path
import asyncio


from ..base.base_tool import tool
from ..llm_api.ollama_llm import OllamaLLM
from ..config.llm_config import LLMConfig
from ..llm_api.base_llm import BaseLLM
from ..utils.utils import Utils

utils = Utils()

CONFIG_DIR_PATH = utils.get_directory("config")

ROOT_DIRECTORY = Path(__file__).parent.parent.parent
DEFAULT_LLM_CONFIG_PATH = str(CONFIG_DIR_PATH / "yaml" / "ollama_config_qwen.yaml")

environment = utils.load_project_env()
DEFAULT_LLM_CONFIG_PATH = environment["LLM_CONFIG_PATH"] if "LLM_CONFIG_PATH" in environment else DEFAULT_LLM_CONFIG_PATH

class EnhanceRetrievalSchema(BaseModel):
    question: str = Field(
        ...,
        description="用户的问题"
    )


@tool
class EnhanceRetrieval:
    end_flag: int = 0
    retrieval: Optional[Retrieval] = None
    args_schema: Type[BaseModel] = EnhanceRetrievalSchema
    llm: Optional[BaseLLM] = None
    retrieval_flag: Optional[bool] = True
    data_dir: Optional[str] = None
    index_dir: Optional[str] = None
    llm_config_path: Optional[str] = None
    
    
    @overload
    def __init__(
        self, 
        end_flag: int = 0,
        retrieval: Optional[Retrieval] = None,
        args_schema: Type[BaseModel] = EnhanceRetrievalSchema,
        llm: Optional[BaseLLM] = None,
        retrieval_flag: Optional[bool] = True,
        data_dir: Optional[str] = None,
        index_dir: Optional[str] = None,
        llm_config_path: Optional[str] = None,
        embedding_model_path: Optional[str] = None
    ):
        ...
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if 'retrieval' in kwargs:
                self.retrieval = kwargs.pop('retrieval')
            if 'llm' in kwargs:
                self.llm = kwargs.pop('llm')
            if 'retrieval_flag' in kwargs:
                self.retrieval_flag = kwargs.pop('retrieval_flag')
            if 'data_dir' in kwargs:
                self.data_dir = kwargs.pop('data_dir')
            if 'index_dir' in kwargs:
                self.index_dir = kwargs.pop('index_dir')
            if 'llm_config_path' in kwargs:
                self.llm_config_path = kwargs.pop('llm_config_path')
            if 'embedding_model_path' in kwargs:
                self.llm_config_path = kwargs.pop('embedding_model_path')
        
            self.retrieval = Retrieval(data_dir=self.data_dir, index_dir=self.index_dir, embedding_model_path=self.embedding_model_path) if self.retrieval is None else self.retrieval
            if self.llm is None:
                try:
                    self.llm_config_path = DEFAULT_LLM_CONFIG_PATH if self.llm_config_path is None else self.llm_config_path
                    self.llm = OllamaLLM(config=LLMConfig.from_file(Path(self.llm_config_path)))
                except Exception as e:
                    raise ValueError(f"Fail to init the llm attribution when init the EnhanceRetrieval class! {str(e)}") from e
        except Exception as e:
            raise ValueError("fail to init the EnhanceRetrieval class! {str(e)}") from e
    
    
    async def execute(
        self, 
        text_list: List[Dict[str, str]], 
        message_history: List[Dict[str, str]] = None,
        top_k: int = 3, 
        question: str = None,
        static_flag: int = 1,
        prompt: Optional[str] = None,
        retrieval_flag: Optional[bool] = True,
        database_retrieval_data: List[Dict[str, str]] = None,
        stream_flag: Optional[bool] = False,
        username: Optional[str] = None
    ):
        if question is None or question == "":
            raise ValueError("Question must not be null!")
        prompt = prompt if prompt is not None else self.system_prompt
        self.retrieval_flag = self.retrieval_flag if retrieval_flag is None else retrieval_flag
        if self.retrieval_flag:
            nodes = await self.retrieval.execute(
                text_list=text_list, 
                top_k=top_k, 
                # top_k=1, 
                retrieval_word=question, 
                static_flag=static_flag
            )
            context_texts = [node.node.text.replace('\n', '') for node in nodes]
            context = "无可用上下文信息" if not context_texts else "\n\n".join(context_texts)
            text_list = context
        else:
            try:
                text_list = str(text_list) if text_list is not None else "无可用上下文信息"
            except Exception as e:
                raise ValueError(f"fail to init text_list! {str(e)}") from e
        database_enhance_prompt = str(database_retrieval_data) if database_retrieval_data is not None else "无可用信息"
        current_time = datetime.now()
        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        message = ""
        if prompt is None:
            message = prompt.format(
                context=text_list,
                current_time=current_time,
                database_enhance_prompt=database_enhance_prompt,
                message_history=message_history,
                question=question
            )
        else:
            message = prompt + f"\n\n上下文信息：\n{text_list}" + f"\n\n当前系统时间：\n{current_time}" + f"\n\n数据库检索内容/检索结果：\n{database_enhance_prompt}" + f"\n\n历史会话消息：\n{message_history}" + f"\n\n用户当前问题：\n{question}"

        namespace_message_history = [{"role": "user", "content": message}]
        if stream_flag == 1:
            # 使用流式输出接口
            chat_stream = self.llm._whoami_text_stream(
                messages=namespace_message_history, 
                timeout=120, 
                user_stop_words=[]
            )
            if not chat_stream:
                self.logger.error("Stream is empty or None!")
                yield "Error: Could not obtain streaming response from LLM."
                return
            try:
                async for chunk in chat_stream:
                    # 只处理非空内容
                    if chunk:
                        # 返回当前块
                        yield chunk
            except Exception as e:
                self.logger.error(f"处理流时出错: {str(e)}")
                yield f"Error: {str(e)}"
        else:
            # 使用非流式输出接口
            try:
                response = await self.llm._whoami_text(messages=namespace_message_history, timeout=30, user_stop_words=[])
                yield response
                return  # 一次性返回完整响应后结束
            except Exception as e:
                self.logger.error(f"非流式处理时出错: {str(e)}")
                yield f"Error: {str(e)}"
                return


if __name__ == '__main__':
    """
    text_list = [
        {"123": "我是卫宇涛，我28，我来自山西运城"}, 
        {"456": "我是卫小涛，30岁，来自山西运城"}, 
        {"789": "我是卫jin涛，30岁，来自山西运城"},
        {"1011": "我是卫jin涛，30岁，来自山西运城"},
        {"1012": "我是卫jin涛，30岁，来自山西运城"},
        {"1013": "我是卫jin涛，30岁，来自山西运城"},
        {"1014": "我是卫jin涛，30岁，来自山西运城"},
    ]
    enhance_retrieval = EnhanceRetrieval()
    
    print(enhance_retrieval)
    async def main():
        generator = enhance_retrieval.execute(
            text_list=text_list,
            database_retrieval_data="我是谁？",
            question="我是谁？",
            stream_flag=True,
            top_k=1
        )
        async for chunk in generator:
            print(chunk)
    asyncio.run(main())
    """
    print(DEFAULT_LLM_CONFIG_PATH)
    
    