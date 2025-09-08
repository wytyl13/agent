#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : data_center.py
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



class DataCenterSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <profile: 查询用户基本信息, statistics：查询统计信息>"
    )
    content: str = Field(
        description="查询内容"
    )


@tool
class DataCenter:
    args_schema: Type[BaseModel] = DataCenterSchema
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
        type,
        content,
        **kwargs
    ) -> Any:
        
        result = ""
        if type == "profile":
            key_mapping = {
                "name": "姓名",
                "age": "年龄",
                "address": "住址",
                "contact": "紧急联系人",
                "health_status": "健康状况",
                "service_type": "服务套餐",
            }
            data_list = [
                {"name": "张秀英", "age": "72岁", "address": "幸福小区3栋201室", "contact": "李想", "health_status": "血压偏高，需定期监测", "service_type": "居家护理+助餐服务"},
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            result = result + "\n" + "<image>/work/ai/agent_chainlit/public/background_big1.png<image>" 
        if type == "statistics":
            key_mapping = {
                "object": "统计项目",
                "value": "数据",
            }
            data_list = [
                {"object": "总接听电话", "value": "1,248通"},
                {"object": "平均接听时长", "value": "3分26秒"},
                {"object": "客户满意度", "value": "98.5%"},
                {"object": "", "value": ""},
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            result += self.format_table_data_markdown(
                type="主要咨询类型分布",
                key_mapping={
                    "main_type": "主要咨询类型",
                    "distribution": "分布情况"
                },
                data_list=[
                    {"main_type": "助餐服务", "distribution": "35%"},
                    {"main_type": "健康咨询", "distribution": "28%"},
                    {"main_type": "维修报修", "distribution": "22%"},
                ]
            )
            
        for item in result:
            yield item
        return
    
if __name__ == '__main__':
    data_center = DataCenter()

    print(data_center.tool_schema)
    