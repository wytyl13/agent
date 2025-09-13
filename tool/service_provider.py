#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : service_provider.py
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



class ServiceProviderSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <LIST: 查询所有服务商信息, STATISTIC: 查看服务商账单信息>"
    )


@tool
class ServiceProvider:
    args_schema: Type[BaseModel] = ServiceProviderSchema
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
        **kwargs
    ) -> Any:
        
        result = ""
        if type == "LIST":
            key_mapping = {
                "provider": "服务商名称",
                "unit_price": "价格",
                "address": "地址",
                "distance": "距离",
                "special_feature": "特色",
                "score": "评分",
                "phone": "电话",
            }
            data_list = [
                {
                    "provider": "爱心家政",
                    "unit_price": "60元/小时起",
                    "address": "阳光路128号",
                    "distance": "800米",
                    "special_feature": "专业老人护理、24小时服务",
                    "score": "4.9",
                    "phone": "400-888-1234"
                },
                {
                    "provider": "贴心家庭",
                    "unit_price": "55元/小时起", 
                    "address": "康乐街45号",
                    "distance": "1.2公里",
                    "special_feature": "深度清洁、家电保养",
                    "score": "4.8",
                    "phone": "400-888-5678"
                },
                {
                    "provider": "温馨到家",
                    "unit_price": "50元/小时起",
                    "address": "和谐大道88号",
                    "distance": "1.5公里", 
                    "special_feature": "钟点工、陪护服务",
                    "score": "4.7",
                    "phone": "400-888-9999"
                },
                {
                    "provider": "金牌管家",
                    "unit_price": "65元/小时起",
                    "address": "民生路36号",
                    "distance": "900米",
                    "special_feature": "高端家政、营养配餐",
                    "score": "4.9",
                    "phone": "400-666-8888"
                },
                {
                    "provider": "安心护理",
                    "unit_price": "58元/小时起",
                    "address": "健康路66号",
                    "distance": "1.1公里",
                    "special_feature": "医护背景、康复护理",
                    "score": "4.8", 
                    "phone": "400-777-6666"
                }
            ]
            result = self.format_table_data_markdown(type="服务商明细", key_mapping=key_mapping, data_list=data_list)
            
        if type == "STATISTIC":
            key_mapping = {
                "bill_id": "账单编号",
                "provider": "服务商名称", 
                "customer_name": "客户姓名",
                "service_type": "服务项目",
                "service_date": "服务日期",
                "service_hours": "服务时长",
                "unit_price": "单价",
                "total_amount": "总金额",
                "payment_status": "支付状态",
                "payment_method": "支付方式",
                "service_address": "服务地址",
                "remarks": "备注"
            }

            # 账单数据列表
            data_list = [
                {
                    "bill_id": "HZ202409001",
                    "provider": "爱心家政",
                    "customer_name": "张秀英",
                    "service_type": "居家护理+助餐服务",
                    "service_date": "2024-09-07",
                    "service_hours": "4小时",
                    "unit_price": "60元/小时",
                    "total_amount": "240元",
                    "payment_status": "已支付",
                    "payment_method": "微信支付",
                    "service_address": "幸福小区3栋201室",
                    "remarks": "血压监测正常，协助用餐"
                },
                {
                    "bill_id": "HZ202409002", 
                    "provider": "贴心家庭",
                    "customer_name": "王老伯",
                    "service_type": "深度清洁服务",
                    "service_date": "2024-09-06",
                    "service_hours": "3小时",
                    "unit_price": "55元/小时", 
                    "total_amount": "165元",
                    "payment_status": "已支付",
                    "payment_method": "支付宝",
                    "service_address": "康乐小区2号楼301",
                    "remarks": "家电保养完成"
                },
                {
                    "bill_id": "HZ202409003",
                    "provider": "温馨到家", 
                    "customer_name": "李奶奶",
                    "service_type": "陪护服务",
                    "service_date": "2024-09-05",
                    "service_hours": "6小时",
                    "unit_price": "50元/小时",
                    "total_amount": "300元", 
                    "payment_status": "待支付",
                    "payment_method": "现金",
                    "service_address": "和谐花园8栋102",
                    "remarks": "陪同就医，心情愉悦"
                },
                {
                    "bill_id": "HZ202409004",
                    "provider": "金牌管家",
                    "customer_name": "陈大爷", 
                    "service_type": "高端家政+营养配餐",
                    "service_date": "2024-09-04",
                    "service_hours": "5小时",
                    "unit_price": "65元/小时",
                    "total_amount": "325元",
                    "payment_status": "已支付", 
                    "payment_method": "银行卡",
                    "service_address": "幸福家园15栋501",
                    "remarks": "制作营养餐，血糖控制良好"
                },
                {
                    "bill_id": "HZ202409005",
                    "provider": "安心护理",
                    "customer_name": "赵阿姨",
                    "service_type": "康复护理", 
                    "service_date": "2024-09-03",
                    "service_hours": "2小时",
                    "unit_price": "58元/小时",
                    "total_amount": "116元",
                    "payment_status": "已支付",
                    "payment_method": "微信支付",
                    "service_address": "阳光社区6栋203",
                    "remarks": "康复训练进展良好"
                }
            ]
            result = self.format_table_data_markdown(type="服务商账单明细", key_mapping=key_mapping, data_list=data_list)
        
        
        for item in result:
            yield item
        return
    