#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : online_market.py
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



class FoodServiceSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <LIST: 查看早餐、午餐、晚餐菜品信息, ORDER: 预定一份菜品, REWARD: 评价某个菜品的口感>"
    )
    content: str = Field(
        description="查询的菜品时段信息，预定的某个菜品名称或评价的某个菜品"
    )


@tool
class FoodService:
    args_schema: Type[BaseModel] = FoodServiceSchema
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
        if type == "LIST":
            # 商品信息字段映射
            key_mapping = {
                "dish_id": "菜品编号",
                "dish_name": "菜品名称",
                "category": "菜品分类",
                "price": "价格", 
                "ingredients": "主要食材",
                "nutrition": "营养特点",
                "availability": "供应状态",
                "rating": "评分",
                "description": "菜品描述",
                "image": "菜品图片"
            }

            # 今日菜单数据
            data_list = [
                {
                    "dish_id": "CD001",
                    "dish_name": "剁椒鸡蛋",
                    "category": "家常菜",
                    "price": "18元",
                    "ingredients": "鸡蛋、剁椒、葱花",
                    "nutrition": "高蛋白、开胃下饭", 
                    "availability": "有货",
                    "rating": "4.6⭐",
                    "description": "嫩滑鸡蛋配香辣剁椒",
                    "image": "[🔗 点击访问]duojiao_jidan.jpg"
                },
                {
                    "dish_id": "CD002", 
                    "dish_name": "清蒸鲈鱼",
                    "category": "蒸菜",
                    "price": "38元",
                    "ingredients": "新鲜鲈鱼、蒸鱼豉油",
                    "nutrition": "低脂高蛋白、易消化",
                    "availability": "有货", 
                    "rating": "4.8⭐",
                    "description": "肉质鲜嫩，营养丰富",
                    "image": "[🔗 点击访问]qingzheng_luyu.jpg"
                },
                {
                    "dish_id": "CD003",
                    "dish_name": "小白菜豆腐汤",
                    "category": "汤品",
                    "price": "12元",
                    "ingredients": "小白菜、嫩豆腐",
                    "nutrition": "清淡养胃、补钙",
                    "availability": "有货",
                    "rating": "4.5⭐", 
                    "description": "清香爽口，老人最爱",
                    "image": "[🔗 点击访问]baicai_doufu.jpg"
                }
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            print(result)
        if type == "ORDER":
            result = """
            🍽️ 助餐订单确认

            订单编号：ZC202409015
            菜品名称：剁椒鸡蛋
            菜品编号：CD001
            份数：1份
            单价：18元/份
            总金额：18元

            👤 客户信息
            客户姓名：张秀英
            送餐地址：幸福小区3栋201室
            联系电话：138****5678

            🕐 用餐安排
            用餐时间：今日午餐
            特殊要求：少放盐，口味清淡
            下单时间：2024-09-08 11:30

            🚚 配送信息
            预计送达：12:00-12:30
            """
        if type == "REWARD":
            result = """
            收到您的评价，我们后续优化菜品口感！
            """
        
        for item in result:
            yield item
        return
    