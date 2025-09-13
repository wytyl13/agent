#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : client_service.py
"""
from typing import (
    Optional,
    Dict,
    Any,
    List,
    overload,
    Type
)

from pydantic import Field, BaseModel


from agent.base.base_tool import tool
from agent.provider.sql_provider import SqlProvider





TABLE_DICT = [
    {"from": "CommunityRealTimeData", "to": "社区实时数据表"},
    {"from": "UserData", "to": "用户数据表"},
]

original_permission = [item["to"] for item in TABLE_DICT]





class BatchExportSchema(BaseModel):

    table_name: str = Field(
        default=None,
        description=f"用户需要导出的数据表名，应该从如下内容中选择其中一个{original_permission}",
    )
    
    role_name: str = Field(
        default=None,
        description="角色名称，如果用户没有提供任何角色名称复制为空白字符串",
    )
    permission: List = Field(
        default=None,
        description=f"权限list，应该从{original_permission}中选择零个、一个或多个权限,",
    )
    is_ensure: int = Field(
        default=None,
        description="用户确认状态：0=首次新增、修改、删除权限请求，需要向用户确认；1=用户已明确确认，可直接执行该指令。只有当用户明确说出'确认'、'同意'、'是的'等确认词汇时才设为1。"
    )


@tool
class BatchExport:
    args_schema: Type[BaseModel] = BatchExportSchema
    end_flag: int = 1
    
    
    @overload
    def __init__(
        self, 
    ):
        ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def format_table_data_markdown(self, type, key_mapping, data_list):
        if not data_list:
            return f"暂无{type}信息"
        
        if key_mapping is None:
            key_mapping = {
            'id': 'ID',
            'name': '姓名',
            'age': '年龄', 
            'type': '类型',
            'content': '内容',
            'create_time': '创建时间',
            'update_time': '更新时间',
            'status': '状态',
            'value': '数值',
            'object': '项目',
            'description': '描述'
        }
            
        # 创建表格标题
        markdown_table = f"### 您好！我已为您查询到{type}的信息：\n\n"
        first_dict = data_list[0] if data_list else {}
        available_keys = list(first_dict.keys())
        
        # 创建表头
        headers = [key_mapping.get(key, key) for key in available_keys]
        markdown_table += "| " + " | ".join(headers) + " |\n"
        markdown_table += "|" + "|".join(["-" * len(header) for header in headers]) + "|\n"
        for i, item in enumerate(data_list, 1):
            row_data = []
            for key in available_keys:
                value = item.get(key, '未知')
                # 处理时间格式
                if 'create_time' in key.lower() and isinstance(value, str) and 'T' in value:
                    date_part, time_part = value.split('T')
                    time_part = time_part.split('.')[0] if '.' in time_part else time_part
                    value = f"{date_part} {time_part}"
                value = str(value).replace('|', '\\|').replace('\n', ' ')
                row_data.append(value)
            
            markdown_table += "| " + " | ".join(row_data) + " |\n"
        
        return markdown_table


    async def execute(
        self,
        type: Optional[str] = None, 
        role_name: Optional[str] = None,
        permission: Optional[str] = None,
        is_ensure: Optional[int] = 0,
        **kwargs
    ) -> Any:

        result = None
        if type and role_name and permission:
            if not type == "查看":
                if is_ensure:
                    result = f"好的，已为您{type}角色{role_name}，{type}后的权限如下： {permission}"
                else:
                    result = f"<text_value>好的，收到{type}：{role_name} * {permission}。</text_value><confirm>请确认是否操作{type}？</confirm>"
            else:
                result = f"好的，角色{role_name}的权限如下：。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。"
        else:
            if not permission:
                result = f"请提供具体的权限！您可以从如下权限中选择：{original_permission}"

            if not type:
                result = f"请提供具体的操作类型！你可以选择如下操作：<新增, 修改, 删除, 查看>"
            
            if not role_name:
                result = "请提供具体的角色名称！"

        for item in result:
            yield item
        return
