#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/26 17:22
@Author  : weiyutao
@File    : planning_agent.py
<follow_up_questions>问题1：</follow_up_questions>
<follow_up_questions>问题2：</follow_up_questions>
<follow_up_questions>问题3：</follow_up_questions>
"""

from typing import (
    Optional,
    Type,
    List,
    Dict,
    Any,
    overload
)
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
import json
import inspect
import asyncio
from contextvars import ContextVar
import uuid
import re

from ..base.base_tool import tool
from .enhance_retrieval import EnhanceRetrieval
from ..llm_api.ollama_llm import OllamaLLM
from ..config.llm_config import LLMConfig
from ..base.base_tool import BaseTool


class FunctionCallSchema(BaseModel):
    question: str = Field(
        ...,
        description="用户需要解决的问题"
    )
    
    tools: List = Field(
        ...,
        description="Agent可以使用的工具域"
    )

    chat_history: List = Field(
        description="对话历史字段"
    )


@tool
class FunctionCall:
    end_flag: int = 0
    args_schema: Type[BaseModel] = FunctionCallSchema
    enhance_llm: EnhanceRetrieval = None
    tools: Optional[List[BaseTool]] = None
    """
    end_flag: 工具调用结束标志符
    args_schema: 参数描述
    enhance_llm: 检索增强生成功能
    tools: 工具调用的工具域
    """


    @overload
    def __init__(
        self,
        enhance_llm: EnhanceRetrieval = None,
        tools: Optional[List[BaseTool]] = None
    ):
        ...


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'enhance_llm' in kwargs:
            self.enhance_llm = kwargs.pop('enhance_llm')

        if 'tools' in kwargs:
            self.tools = kwargs.pop('tools')
    
        if self.enhance_llm is None:
            raise ValueError("EnhanceLLM must not be null!")

        if self.tools:
            self.tool_call_json = [tool.tool_schema for tool in self.tools]
            self.logger.info(self.tool_call_json)


    async def agent_execute(
        self, 
        query, 
        messages,
    ):
        """
        query: str = "用户输入"
        messages: List[Dict[str, str]] = [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": ""},
            {"role": "function_call", "content": ""},
            {"role": "observation", "content": ""}
        ]
        return: stream string
        """
        messages = messages if messages else []
        if query:
            messages.append(
                {"role": "user", "content": query}
            )
        self.logger.info(f"wait for the return of llm:----------------------\n\n{messages}")
        try:
            # 后续优化RAG使用enhance_llm
            response = await self.enhance_llm.llm._whoami_text(
                messages=messages,
                timeout=12,
                use_tool=True,
                temperature=0.0,
                tool_call_json=self.tool_call_json
            )
            if not response:
                raise Exception("工具调用模块返回为空")
            
            self.logger.info(f"LLM return:----------------------\n{response}\n\n")
            result = re.search("<tool_call>\n(.*?)\n</tool_call>", response, re.DOTALL)
            if result:  
                messages.append({"role": "function_call", "content": response})
                tool_json_string = result.group(1)
                tool_json = json.loads(tool_json_string)
                tool_name = tool_json['name']
                tool_arguments = tool_json['arguments']
                self.logger.info(f"function call parameters extracted information:----------------------\n{tool_name, tool_arguments}\n\n")

                the_tool = None
                for t in self.tools:
                    if t.name in tool_name:
                        the_tool = t
                        break
                
                tool_name = the_tool.name
                chunks = []
                async for chunk in the_tool.execute(**tool_arguments):
                    chunks.append(chunk)
                    if the_tool.end_flag == 1:
                        yield chunk
                tool_result = ''.join(chunks)
                self.logger.info(f"tool executed result:----------------------\n{tool_result}\n\n")
                
                if the_tool.end_flag == 0:
                    messages.append(
                        {"role": "function_call", "content": tool_json_string}
                    )
                    messages.append(
                        {"role": "observation", "content": tool_result}
                    )
                    # 递归调用，继续处理
                    async for chunk in self.agent_execute("", messages):
                        yield chunk
                return
            else:
                yield response
                return
        except Exception as e:
            print(f"发生错误: {str(e)}") 
            self._set_status("error", f"发生错误: {str(e)}")
            yield f"发生错误: {str(e)}", []
            return # 这里直接返回，避免重复抛出异常


    async def execute(
        self, 
        tools: Optional[list[any]] = None,
        question: str = None,
        messages: Optional[List] = None,
    ):
        if tools:
            self.tools = tools
            self.tool_call_json = [tool.tool_schema for tool in self.tools]
        else:
            if not self.tools:
                raise ValueError("tools must not be null!")

        async for chunk in self.agent_execute(
            query=question,
            messages=messages or [],
        ):
            yield chunk


if __name__ == '__main__':
    
    from .client_service import ClientService
    from .order import Order
    from .role import Role
    
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
    tools = [client_service, order, role]
    function_call = FunctionCall(
        tools = [client_service, order, role],
        enhance_llm=enhance_qwen_admin,
    )


    async def main():
        result = None
        history_message = None
        
        # function_call_case_1
        # tools = [client_service, order, role]
        # messages=[
        #     {"role": "user", "content": "帮我预定1份鸡蛋"},
        #     {"role": "assistant", "content": "好的，收到订单：鸡蛋 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
        #     {"role": "user", "content": "确认"},
        #     {"role": "assistant", "content": "好的，已经帮您预定鸡蛋 * 1"},
        #     {"role": "user", "content": "帮我预定1杯牛奶"},
        #     {"role": "assistant", "content": "好的，收到订单：牛奶 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
        #     {"role": "user", "content": "取消"},
        #     {"role": "assistant", "content": "好的，没有为您下订单。如果您改变主意，请告诉我。"},
        # ]
        
        
        # function_call_case_2
        tools = [client_service, order, role]
        messages=[
            {"role": "user", "content": "我要新增一个角色"},
            {"role": "assistant", "content": "请提供具体的角色名称！"},
            {"role": "user", "content": "产品经理"},
            {"role": "assistant", "content": "请提供具体的权限！您可以从如下权限中选择：['服务项目管理', '商品分类管理', '设备类别管理']"},
            {"role": "user", "content": "服务项目和商品分类"},
            {"role": "assistant", "content": "<text_value>好的，收到新增：产品经理 * ['服务项目管理', '商品分类管理']。</text_value><confirm>请确认是否操作新增？</confirm>"},
        ]
        
        chunks = []
        async for chunk in function_call.execute(
            question="确认",
            messages=messages,
            tools=tools
        ):
            chunks.append(chunk)
        result = ''.join(chunks)
        print(result)

    asyncio.run(main())