#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/09/04 14:04
@Author  : weiyutao
@File    : course_service.py
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



class CourseServiceSchema(BaseModel):

    type: str = Field(
        description="查询类型: str = <COURSE: 查询老年大学课程, ENROLL: 报名某一个课程, PROGRESS: 查看出勤情况>"
    )
    content: str = Field(
        description="查询的课程名称、报名的课程名称或者查询的出勤时间"
    )


@tool
class CourseService:
    args_schema: Type[BaseModel] = CourseServiceSchema
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
        if type == "COURSE":
            # 课程信息字段映射
            key_mapping = {
                "course_id": "课程编号",
                "course_name": "课程名称",
                "course_type": "课程类型",
                "instructor": "授课老师",
                "schedule": "上课时间",
                "location": "上课地点",
                "capacity": "课程容量",
                "enrolled": "已报名人数",
                "status": "报名状态",
                "duration": "课程时长",
                "description": "课程描述"
            }

            # 课程数据列表
            data_list = [
                {
                    "course_id": "CS001",
                    "course_name": "太极拳基础班",
                    "course_type": "健身运动",
                    "instructor": "王师傅",
                    "schedule": "周一、周三 09:00-10:30",
                    "location": "活动中心一楼",
                    "capacity": "20人",
                    "enrolled": "15人",
                    "status": "可报名",
                    "duration": "8周课程",
                    "description": "适合初学者，注重基础动作和呼吸配合"
                },
                {
                    "course_id": "CS002",
                    "course_name": "太极拳提高班",
                    "course_type": "健身运动",
                    "instructor": "王师傅",
                    "schedule": "周二、周四 09:00-10:30",
                    "location": "活动中心一楼",
                    "capacity": "15人",
                    "enrolled": "12人",
                    "status": "可报名",
                    "duration": "8周课程",
                    "description": "有基础学员，学习复杂套路和实战技巧"
                },
                {
                    "course_id": "CS003",
                    "course_name": "毛笔书法入门",
                    "course_type": "文化艺术",
                    "instructor": "李老师",
                    "schedule": "周一、周五 14:00-15:30",
                    "location": "文化活动室",
                    "capacity": "12人",
                    "enrolled": "8人",
                    "status": "可报名",
                    "duration": "10周课程",
                    "description": "从基本笔画开始，学习楷书基础"
                },
                {
                    "course_id": "CS004",
                    "course_name": "硬笔书法班",
                    "course_type": "文化艺术",
                    "instructor": "李老师",
                    "schedule": "周三、周六 14:00-15:30",
                    "location": "文化活动室",
                    "capacity": "15人",
                    "enrolled": "15人",
                    "status": "已满员",
                    "duration": "8周课程",
                    "description": "钢笔字练习，提高日常书写水平"
                },
                {
                    "course_id": "CS005",
                    "course_name": "养生气功",
                    "course_type": "健身运动",
                    "instructor": "张教练",
                    "schedule": "周二、周四 08:00-09:00",
                    "location": "户外广场",
                    "capacity": "25人",
                    "enrolled": "20人",
                    "status": "可报名",
                    "duration": "12周课程",
                    "description": "八段锦、五禽戏等传统养生功法"
                },
                {
                    "course_id": "CS006",
                    "course_name": "国画山水班",
                    "course_type": "文化艺术",
                    "instructor": "陈老师",
                    "schedule": "周六 09:00-11:00",
                    "location": "美术教室",
                    "capacity": "10人",
                    "enrolled": "7人",
                    "status": "可报名",
                    "duration": "12周课程",
                    "description": "学习山水画基本技法和意境表达"
                }
            ]

            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
            
        if type == f"ENROLL":
            result = f"""
            好的，已帮您预定{content}！请注意您的时间安排：
            """
        
        if type == "PROGRESS":
            # 学员出勤记录数据结构（用于查询出勤情况）
            key_mapping = {
                "student_id": "学员编号",
                "student_name": "学员姓名",
                "course_id": "课程编号",
                "course_name": "课程名称",
                "attendance_date": "上课日期",
                "check_in_time": "签到时间",
                "status": "出勤状态",
                "month": "月份"
            }

            # 出勤记录示例数据
            data_list = [
                {
                    "student_id": "ST001",
                    "student_name": "张大爷",
                    "course_id": "CS001",
                    "course_name": "太极拳基础班",
                    "attendance_date": "2024-12-02",
                    "check_in_time": "08:55",
                    "status": "已签到",
                    "month": "2024-12"
                },
                {
                    "student_id": "ST001",
                    "student_name": "张大爷",
                    "course_id": "CS001",
                    "course_name": "太极拳基础班",
                    "attendance_date": "2024-12-04",
                    "check_in_time": "09:10",
                    "status": "迟到",
                    "month": "2024-12"
                },
                {
                    "student_id": "ST001",
                    "student_name": "张大爷",
                    "course_id": "CS003",
                    "course_name": "毛笔书法入门",
                    "attendance_date": "2024-12-06",
                    "check_in_time": "13:58",
                    "status": "已签到",
                    "month": "2024-12"
                },
                {
                    "student_id": "ST001",
                    "student_name": "张大爷",
                    "course_id": "CS001",
                    "course_name": "太极拳基础班",
                    "attendance_date": "2024-12-09",
                    "check_in_time": "",
                    "status": "缺勤",
                    "month": "2024-12"
                }
            ]
            result = self.format_table_data_markdown(type=content, key_mapping=key_mapping, data_list=data_list)
        
        for item in result:
            yield item
        return
    