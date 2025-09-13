#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : subsidy_service.py
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



class SubsidyServiceSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <BALANCE: 余额查询, SERVICE: 补贴可兑换的服务查询, REDEEM: 兑换相应的补贴服务>"
    )
    content: str = Field(
        description="查询类型或需要兑换的服务名称"
    )


@tool
class SubsidyService:
    args_schema: Type[BaseModel] = SubsidyServiceSchema
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
        if type == "BALANCE":
            # 课程信息字段映射
            key_mapping = {
                "user_id": "用户编号",
                "user_name": "用户姓名",
                "subsidy_type": "补贴类型",
                "total_amount": "补贴总额",
                "used_amount": "已使用金额",
                "remaining_amount": "剩余金额",
                "validity_period": "有效期",
                "last_update": "最后更新时间"
            }

            # 课程数据列表
            data_list = [
                {
                    "user_id": "U001",
                    "user_name": "李大爷",
                    "subsidy_type": "养老服务补贴",
                    "total_amount": "2000元",
                    "used_amount": "650元",
                    "remaining_amount": "1350元",
                    "validity_period": "2024年12月31日",
                    "last_update": "2024-12-01"
                },
                {
                    "user_id": "U001", 
                    "user_name": "李大爷",
                    "subsidy_type": "医疗康复补贴",
                    "total_amount": "1500元",
                    "used_amount": "300元",
                    "remaining_amount": "1200元",
                    "validity_period": "2024年12月31日",
                    "last_update": "2024-11-28"
                },
                {
                    "user_id": "U001",
                    "user_name": "李大爷", 
                    "subsidy_type": "居家护理补贴",
                    "total_amount": "3000元",
                    "used_amount": "800元",
                    "remaining_amount": "2200元",
                    "validity_period": "2024年12月31日",
                    "last_update": "2024-11-25"
                }
            ]

            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            
        if type == f"REDEEM":
            result = f"""
            好的，已帮您预定{content}！您可以尝试询问我的补贴什么时候到账来查看补贴申请进度！
            """
        
        if type == "SERVICE":
            # 学员出勤记录数据结构（用于查询出勤情况）
            key_mapping = {
                "service_id": "服务编号",
                "service_name": "服务名称",
                "service_category": "服务分类",
                "provider": "服务提供方",
                "unit_price": "单价",
                "service_unit": "服务单位",
                "applicable_subsidy": "适用补贴类型",
                "service_duration": "服务时长",
                "availability": "可用状态",
                "description": "服务描述",
                "rating": "服务评分"
            }

            # 出勤记录示例数据
            data_list = [
                {
                    "service_id": "SV001",
                    "service_name": "居家护理服务",
                    "service_category": "护理照料",
                    "provider": "阳光护理中心",
                    "unit_price": "80元",
                    "service_unit": "小时",
                    "applicable_subsidy": "居家护理补贴",
                    "service_duration": "2-8小时/次",
                    "availability": "可预约",
                    "description": "专业护理人员上门提供日常护理、用药提醒、健康监测等服务",
                    "rating": "4.8⭐"
                },
                {
                    "service_id": "SV002",
                    "service_name": "助餐配送服务",
                    "service_category": "生活照料", 
                    "provider": "爱心餐厅",
                    "unit_price": "25元",
                    "service_unit": "餐",
                    "applicable_subsidy": "养老服务补贴",
                    "service_duration": "一日三餐",
                    "availability": "可预约",
                    "description": "营养均衡的老年餐配送，支持特殊饮食需求",
                    "rating": "4.6⭐"
                },
                {
                    "service_id": "SV003",
                    "service_name": "家政清洁服务",
                    "service_category": "生活照料",
                    "provider": "家洁保洁公司",
                    "unit_price": "60元",
                    "service_unit": "小时",
                    "applicable_subsidy": "养老服务补贴",
                    "service_duration": "2-4小时/次",
                    "availability": "可预约",
                    "description": "室内清洁、衣物整理、简单家务等服务",
                    "rating": "4.5⭐"
                },
                {
                    "service_id": "SV004",
                    "service_name": "康复理疗服务",
                    "service_category": "医疗康复",
                    "provider": "康复医疗中心",
                    "unit_price": "120元",
                    "service_unit": "次",
                    "applicable_subsidy": "医疗康复补贴",
                    "service_duration": "45-60分钟/次",
                    "availability": "可预约",
                    "description": "物理治疗、按摩推拿、功能训练等康复服务",
                    "rating": "4.9⭐"
                },
                {
                    "service_id": "SV005",
                    "service_name": "代购代办服务",
                    "service_category": "生活照料",
                    "provider": "便民服务站",
                    "unit_price": "30元",
                    "service_unit": "次",
                    "applicable_subsidy": "养老服务补贴",
                    "service_duration": "1-2小时/次",
                    "availability": "可预约",
                    "description": "日用品代购、药品代取、证件代办等便民服务",
                    "rating": "4.4⭐"
                },
                {
                    "service_id": "SV006",
                    "service_name": "心理咨询服务",
                    "service_category": "精神慰藉",
                    "provider": "心理健康中心",
                    "unit_price": "100元",
                    "service_unit": "次",
                    "applicable_subsidy": "养老服务补贴",
                    "service_duration": "50分钟/次",
                    "availability": "可预约",
                    "description": "专业心理咨询师提供情感疏导、心理支持等服务",
                    "rating": "4.7⭐"
                },
                {
                    "service_id": "SV007",
                    "service_name": "上门体检服务",
                    "service_category": "医疗康复",
                    "provider": "社区卫生服务中心",
                    "unit_price": "200元",
                    "service_unit": "次",
                    "applicable_subsidy": "医疗康复补贴",
                    "service_duration": "1-2小时/次",
                    "availability": "可预约",
                    "description": "基础体检、血压血糖监测、健康评估等服务",
                    "rating": "4.6⭐"
                }
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
        
        for item in result:
            yield item
        return
    