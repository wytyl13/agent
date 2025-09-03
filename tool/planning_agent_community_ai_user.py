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
    Dict
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

class PlanningAgentCommunityAiUserSchema(BaseModel):
    question: str = Field(
        ...,
        description="用户需要解决的问题"
    )
    
    tools: List = Field(
        ...,
        description="Agent可以使用的工具域"
    )
    



@tool
class PlanningAgentCommunityAiUser:
    end_flag: int = 0
    args_schema: Type[BaseModel] = PlanningAgentCommunityAiUserSchema
    enhance_llm: Optional[EnhanceRetrieval] = None
    tools: Optional[List[BaseTool]] = None
    tool_descs: Optional[str] = None
    tool_names: Optional[str] = None
    
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
            raise ValueError("Fail to init the tool_descs and tool_names!")
    
    
    async def agent_execute(
        self, 
        query, 
        chat_history, 
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
            chat_history.append({"role":"user","content":query})
            messages = chat_history
            return_message = chat_history.copy()

        else:
            messages = []
            return_message = []
            messages.append({"role": "user", "content": query})
            return_message.append({"role": "user", "content": query})


        self.logger.info(f"---等待LLM返回... ...\n{messages}")
        try:
            response = await self.enhance_llm.llm._whoami_text(messages=messages, timeout=360,use_tool=True)
            if not response:
               raise Exception("工具调用模块返回为空")
            self.logger.info(f"---LLM返回... ...\n{response}")


            result = re.match("<tool_call>\n(.*)\n</tool_call>",response)
            if result:  
                messages.append({"role": "function_call", "content": response})
                tool_json_string = result.group(1)
                tool_json = json.loads(tool_json_string)
                tool_name = tool_json['name']
                # tool_arguments = json.loads(tool_json['arguments'].replace("'",'"'))
                tool_arguments = tool_json['arguments']
                self.logger.info(f"=============工具调用提取的参数信息============={tool_name, tool_arguments}")
                # 5 匹配tool
                yield f"=============工具调用提取的参数信息============={tool_name, tool_arguments}", messages
                
                # the_tool = None
                # for t in self.tools:
                #     # if t.name == action: # 使用更加严格的工具匹配
                #     if t.name in tool_name:
                #         the_tool = t
                #         break
                # tool_name = the_tool.name



            # 6 执行tool
            
                # 注意上一步工具的输出结果最好不要有嵌套json，否则解析会出错
                # 因为大语言模型对嵌套json字符串的返回不是转义格式，这不符合python中的json工具对json字符串的解析要求
                # signature = inspect.signature(the_tool.execute)
                # if "message_history" in signature.parameters or any(
                #     param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL) 
                #     for param in signature.parameters.values()
                # ):
                #     tool_arguments["message_history"] = []
                
                # tool_arguments["username"] = username
                # tool_arguments["location"] = location
                # tool_arguments["role"] = role
                # self.logger.info(f"tool_arguments: ----------------------------------------- {tool_arguments}")
                
                # tool_ret = ""
                # if the_tool.end_flag == 1:
                    
                #     async for chunk in the_tool.execute(**tool_arguments):
                #         yield chunk, return_message
                        
                #         tool_ret += chunk
                #     self._set_status("success")
                #     self.logger.info(f"---执行tool结果... ...\n{tool_ret}")
                #     # chat_history.append((query, tool_ret))
                # else:
                #     tool_ret = await the_tool.execute(**tool_arguments)
                #     self.logger.info(f"---执行tool结果... ...\n{tool_ret}")
                # messages.append({"role": "observation", "content": tool_ret})
                # final_response = tool_ret
                # # final_response = await  self.enhance_llm.llm._whoami_text(messages=messages, timeout=30, use_tool=True)
                # # chat_history.append((query, final_response))
                # return_message.append({"role": "assistant", "content": tool_ret})
                # self._set_status("success")
                # yield final_response,return_message
            else:
                return_message.append({"assistant": "assistant", "content":response})
                yield response,return_message
                return      
                
        except Exception as e:
            print(f"发生错误: {str(e)}") 
            self._set_status("error", f"发生错误: {str(e)}")
            yield f"发生错误: {str(e)}", []
            raise Exception


                


    
    async def execute(
        self, 
        tools: Optional[list[any]] = None,
        question: str = None,
        chat_history: Optional[List] = None,
        retry_times: Optional[int] = 3,
        retrieval_flag: Optional[bool] = True,
        username: str = None,
        location: str = None,
        role: str = None
    ):
        if tools:
            self.tools = tools
            self._init_descs_names()


        async for chunk in self.agent_execute(
            query=question,
            chat_history=chat_history or [],
            retrieval_flag=retrieval_flag,
            retry_count=0,
            max_retries=retry_times,
            username=username,
            location=location,
            role=role
        ):
            yield chunk