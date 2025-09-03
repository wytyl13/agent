#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/05/07 10:44
@Author  : weiyutao
@File    : sleep_indices_extract.py
"""

from typing import (
    Any
)
from datetime import datetime
from ..base.base_tool import tool
from ..tool.info_extract import InfoExtract

@tool
class SleepIndicesExtract(InfoExtract):
    """睡眠指标关键字提取
    从用户输入的内容中提取需要查询的睡眠报告相关的关键字
    Args:
        InfoExtract (_type_): _description_
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'llm' in kwargs:
            self.llm = kwargs.get('llm')
            
        if 'default_extract_result' in kwargs:
            self.default_extract_result = kwargs.get('default_extract_result')
            
        if 'field_description' in kwargs:
            self.field_description = kwargs.get('field_description')
            
        self.system_prompt = self.system_prompt.replace("{field_description}", str(self.field_description))


if __name__ == '__main__':
    from ..provider.sql_provider import SqlProvider
    from ..llm_api.ollama_llm import OllamaLLM
    from ..config.llm_config import LLMConfig
    from pathlib import Path
    
    
