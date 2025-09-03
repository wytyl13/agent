#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/26 17:22
@Author  : weiyutao
@File    : planning_agent.py
"""

from typing import (
    Optional,
    Type,
    List,
    Dict,
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
from ..tool.enhance_retrieval import EnhanceRetrieval
from ..llm_api.ollama_llm import OllamaLLM
from ..config.llm_config import LLMConfig
from ..base.base_tool import BaseTool



execution_context: ContextVar[dict] = ContextVar('execution_context')

class PlanningAgentCommunityAiAdminSchema(BaseModel):
    question: str = Field(
        ...,
        description="用户需要解决的问题"
    )
    
    tools: List = Field(
        ...,
        description="Agent可以使用的工具域"
    )
    

@tool
class PlanningAgentCommunityAiAdmin:
    end_flag: int = 0
    args_schema: Type[BaseModel] = PlanningAgentCommunityAiAdminSchema
    enhance_llm: Optional[EnhanceRetrieval] = None
    tools: Optional[List[BaseTool]] = None
    tool_descs: Optional[str] = None
    tool_names: Optional[str] = None
    
    @overload
    def __init(
        self, 
        enhance_llm,
        tools
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
            self._init_descs_names()


    def _get_context(self):
        """获取当前执行上下文"""
        try:
            return execution_context.get()
        except LookupError:
            # 如果没有上下文，创建一个新的
            ctx = {
                "execution_id": str(uuid.uuid4()),
                "status": "ready",
                "error_message": ""
            }
            execution_context.set(ctx)
            return ctx

    
    def _set_status(self, status: str, error_message: str = ""):
        """设置执行状态"""
        ctx = self._get_context()
        ctx["status"] = status
        ctx["error_message"] = error_message


    def _init_descs_names(self):
        """初始化工具描述信息

        Returns:
            _type_: _description_
        """
        try:
            # tool_descs = [str(t.tool_schema) for t in self.tools]
            tool_descs = [t.get_simple_tool_description() for t in self.tools]
            self.tool_descs = '\n\n'.join(tool_descs)
            self.tool_names = ', '.join([tool.name for tool in self.tools])
        except Exception as e:
            raise ValueError(f"Fail to init the tool_descs and tool_names!{str(e)}")
    
    
    async def agent_execute(
        self, 
        query, 
        chat_history=[], 
        retrieval_flag=False, 
        retry_count=0, 
        max_retries=3,
        username: str = None,
        location: str = None,
        role: str = None,

    ):
        
        
        # 初始化上下文
        self._set_status("running")
        
        global tools, tool_names, tool_descs, system_prompt, llm, tokenizer

        if chat_history:
            messages = chat_history
        else:
            messages = []
            messages.append({"role": "user", "content": query})


        self.logger.info(f"---等待LLM返回... ...\n{messages}")

        response = await self.enhance_llm.llm._whoami_tool(messages=messages, timeout=30)
        messages.append({"role": "function_call", "content": json.dumps(response)})

        self.logger.info(f"---LLM返回... ...\n{response}")


        result = re.match("<tool_call>\n(.*)\n</tool_call>",response)
        if result:
            try:    
                tool_json_string = result.group(1)
                tool_json = json.loads(tool_json_string)
                tool_name = tool_json['name']
                tool_arguments = tool_json['arguments']
                self.logger.info(f"=============工具调用提取的参数信息============={tool_name, tool_arguments}")
                # 5 匹配tool
                the_tool = None
                for t in self.tools:
                    # if t.name == action: # 使用更加严格的工具匹配
                    if t.name in tool_name:
                        the_tool = t
                        break
                tool_name = the_tool.name



            # 6 执行tool
            
                # 注意上一步工具的输出结果最好不要有嵌套json，否则解析会出错
                # 因为大语言模型对嵌套json字符串的返回不是转义格式，这不符合python中的json工具对json字符串的解析要求
                signature = inspect.signature(the_tool.execute)
                if "message_history" in signature.parameters or any(
                    param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL) 
                    for param in signature.parameters.values()
                ):
                    tool_arguments["message_history"] = messages
                
                tool_arguments["username"] = username
                tool_arguments["location"] = location
                tool_arguments["role"] = role
                self.logger.info(f"tool_arguments: ----------------------------------------- {tool_arguments}")
                
                tool_ret = ""
                if the_tool.end_flag == 1:
                    
                    async for chunk in the_tool.execute(**tool_arguments):
                        yield chunk, messages
                        
                        tool_ret += chunk
                    self._set_status("success")
                    self.logger.info(f"---执行tool结果... ...\n{tool_ret}")
               
                else:
                    tool_ret = await the_tool.execute(**tool_arguments)
                    self.logger.info(f"---执行tool结果... ...\n{tool_ret}")
                messages.append({"role": "observation", "content": tool_ret})
                
                final_response = await  self.enhance_llm.llm._whoami_tool(messages=messages, timeout=30)
                
                messages.append([{"role": "assistant", "content": final_response}])
                self._set_status("success")
                yield final_response,messages
                
                
            except Exception as e:
                print(f"发生错误: {str(e)}") 
                self._set_status("error", f"发生错误: {str(e)}")
                yield f"发生错误: {str(e)}", []

        else:
            messages.append({"assistant": "assistant", "content":response})
            yield response,messages
            return
    
    
    async def execute(
        self, 
        tools: Optional[list[any]] = None,
        question: str = None,
        chat_history: Optional[List] = None,
        retry_times: Optional[int] = 3,
        retrieval_flag: Optional[bool] = True,
        username: str = None,
        location: str = None,
        role: str = None,
    ):
        if tools:
            self.tools = tools
            self._init_descs_names()
        self.logger.info("username: ----------------------------------- {username}")
        async for chunk in self.agent_execute(
            query=question,
            chat_history=chat_history or [],
            retrieval_flag=retrieval_flag,
            retry_count=0,
            max_retries=retry_times,
            username=username,
            location=location,
            role=role,
        ):
            yield chunk



# if __name__ == '__main__':
#     from ..llm_api.ollama_llm import OllamaLLM
#     from ..config.llm_config import LLMConfig
#     from ..tool.direct_llm_community_ai_admin import DirectLLMCommunityAiAdmin
#     from ..tool.direct_llm_community_ai_user import DirectLLMCommunityAiUser
#     from ..tool.google_search import GoogleSearch
#     from ..tool.weather_api import WeatherApi
#     from ..tool.retrieval import Retrieval
#     from ..tool.enhance_retrieval import EnhanceRetrieval
#     from ..tool.handle_shixun_tonggao import HandleTongzhiTonggao
#     from ..tool.water_machine_api import WaterMachineApi
#     from ..config.sql_config import SqlConfig
#     from ..tool.enhance_retrieval import DEFAULT_LLM_CONFIG_PATH
#     from ..tool.retrieval import DEFAULT_RETRIEVAL_DATA_PATH
#     from ..tool.retrieval import DEFAULT_RETRIEVAL_STORAGE_PATH
    
#     enhance_qwen_admin = EnhanceRetrieval(retrieval_flag=False, data_dir=DEFAULT_RETRIEVAL_DATA_PATH, index_dir=DEFAULT_RETRIEVAL_STORAGE_PATH)
#     retrieval = Retrieval(data_dir=DEFAULT_RETRIEVAL_DATA_PATH, index_dir=DEFAULT_RETRIEVAL_STORAGE_PATH)
#     direct_llm_tool = DirectLLMCommunityAiAdmin(enhance_llm=enhance_qwen_admin)
#     direct_llm_tool_user = DirectLLMCommunityAiUser(enhance_llm=enhance_qwen_admin)
#     google_search_tool = GoogleSearch(retrieval=retrieval)
#     weather_api = WeatherApi()
#     handle_tongzhi_tonggao = HandleTongzhiTonggao(enhance_llm=enhance_qwen_admin)
#     water_machine_api = WaterMachineApi()
#     planning_agent = PlanningAgentCommunityAiAdmin(
#         tools=[direct_llm_tool, weather_api, handle_tongzhi_tonggao],
#         enhance_llm=enhance_qwen_admin
#     )
    
#     async def main():
#         async for chunk in planning_agent.agent_execute(
#             query="你是谁"
#         ):
#             print(chunk)
            
            
#     import asyncio
#     asyncio.run(main())
    
    
    

