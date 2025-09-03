#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/24 10:27
@Author  : weiyutao
@File    : sql_config.py
"""



import yaml
import os
from typing import Dict, Optional, Union
from enum import Enum
from typing import Optional, Dict, Any
import argparse
from pathlib import Path

from ..utils.yaml_model import YamlModel
from ..utils.log import Logger

ROOT_DIRECTORY = Path(__file__).parent.parent
CONFIG_PATH = str(ROOT_DIRECTORY / "config" / "yaml" / "sql_config_case.yaml")

logger = Logger('SqlConfig')

class SqlConfig(YamlModel):
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    table: Optional[str] = None
    database_type: Optional[str] = None
    
    
    @property
    def sql_url(self) -> str:
        """
        根据数据库类型返回对应的异步连接URL
        """
        if self.database_type == 'postgresql' or self.database_type == 'postgres':
            return self.postgres_url
        elif self.database_type == 'mysql':
            return self.mysql_url
        else:
            raise ValueError(f"不支持的数据库类型: {self.database_type}")


    @property
    def postgres_url(self) -> str:
        """
        返回PostgreSQL异步连接URL
        """
        if not all([self.host, self.port, self.username, self.password, self.database]):
            raise ValueError("PostgreSQL连接缺少必要参数: host, port, username, password, database")
        
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


    @property
    def mysql_url(self) -> str:
        """
        返回MySQL异步连接URL
        """
        if not all([self.host, self.port, self.username, self.password, self.database]):
            raise ValueError("MySQL连接缺少必要参数: host, port, username, password, database")
        
        return f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str, default=CONFIG_PATH, help='the default sql config path!')
    args = parser.parse_args()
    detector_config = SqlConfig.from_file().__dict__
    try:
        with open(args.file_path, "w") as yaml_file:
            yaml.dump(detector_config, yaml_file)
        logger.info(f"success to init the default config yaml file path!{args.file_path}")
    except Exception as e:
        raise ValueError(f"invalid file path!{args.file_path}") from e