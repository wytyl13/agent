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



class OnlineMarketSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <LIST: 查询某一商品的在售信息, ORDER: 预定某一商品, TRANSPORTATION: 查看某个商品的物流信息>"
    )
    content: str = Field(
        description="查询的内容"
    )


@tool
class OnlineMarket:
    args_schema: Type[BaseModel] = OnlineMarketSchema
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
                "product_id": "商品编号",
                "product_name": "商品名称", 
                "brand": "品牌",
                "specification": "规格",
                "price": "价格",
                "stock": "库存",
                "rating": "评分",
                "sales": "销量",
                "description": "商品描述"
            }

            # 尿不湿商品数据
            data_list = [
                {
                    "product_id": "SP001",
                    "product_name": "成人护理垫", 
                    "brand": "安而康",
                    "specification": "L码/10片装",
                    "price": "39.9元",
                    "stock": "充足",
                    "rating": "4.8⭐",
                    "sales": "月销1200+",
                    "description": "超强吸收，透气舒适"
                },
                {
                    "product_id": "SP002", 
                    "product_name": "成人纸尿裤",
                    "brand": "添宁",
                    "specification": "M码/8片装", 
                    "price": "45.8元",
                    "stock": "充足",
                    "rating": "4.9⭐",
                    "sales": "月销890+",
                    "description": "夜用加长，防漏侧边"
                },
                {
                    "product_id": "SP003",
                    "product_name": "护理垫",
                    "brand": "包大人",
                    "specification": "XL码/12片装",
                    "price": "52.0元", 
                    "stock": "库存紧张",
                    "rating": "4.7⭐",
                    "sales": "月销650+",
                    "description": "加厚设计，12小时干爽"
                }
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            
        if type == "ORDER":
            result = """
            已帮您预定商品：
            📋 订单确认信息

            订单编号：DD202409008
            商品名称：护理垫
            商品编号：SP003
            购买数量：2包
            单价：52.0元/包
            总价：104.0元

            👤 客户信息
            客户姓名：张秀英
            配送地址：幸福小区3栋201室
            联系电话：138****5678

            💳 支付信息
            支付方式：微信支付
            下单时间：2024-09-08 14:30

            🚚 配送信息
            预计送达：明天上午10:00-12:00
            """
        
        if type == "TRANSPORTATION":
            key_mapping = {
                "order_id": "订单编号",
                "product_name": "商品名称",
                "product_id": "商品编号", 
                "quantity": "购买数量",
                "unit_price": "单价",
                "total_price": "总价",
                "customer_name": "客户姓名",
                "delivery_address": "配送地址",
                "contact_phone": "联系电话",
                "payment_method": "支付方式",
                "order_time": "下单时间",
                "estimated_delivery": "预计送达"
            }

            # 订单确认数据
            data_list = [
                {
                    "order_id": "DD202409008",
                    "product_name": "护理垫",
                    "product_id": "SP003",
                    "quantity": "2包",
                    "unit_price": "52.0元/包", 
                    "total_price": "104.0元",
                    "customer_name": "张秀英",
                    "delivery_address": "幸福小区3栋201室",
                    "contact_phone": "138****5678",
                    "payment_method": "微信支付",
                    "order_time": "2024-09-08 14:30",
                    "estimated_delivery": "明天上午10:00-12:00"
                }
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
        
        for item in result:
            yield item
        return
    