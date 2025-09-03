#!/usr/bin/env python3
"""
简单的项目初始化工具
"""
import os
import sys
from pathlib import Path


def create_config_files(target_dir=".", template_files=None, init_dirs=None):
    """
    在目标目录创建配置文件和目录
    
    Args:
        target_dir: 目标目录
        template_files: 字典 {'文件路径': '文件内容', 'config/test.yaml': 'yaml内容...'}
        init_dirs: 目录列表 ['config', 'logs', 'tools']
    """
    target_path = Path(target_dir)
    
    # 1. 创建目录
    if init_dirs:
        for dir_name in init_dirs:
            dir_path = target_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_name}/")
    
    # 2. 创建文件
    if template_files:
        for target_file_path, source_file_path in template_files.items():
            # 读取源文件内容
            try:
                source_path = Path(source_file_path)
                if not source_path.exists():
                    print(f"Warning: 源文件不存在: {source_file_path}")
                    continue
                
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 创建目标文件
                full_path = target_path / target_file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 检查目标文件是否存在
                if full_path.exists():
                    response = input(f"文件 {target_file_path} 已存在，是否覆盖? (y/N): ")
                    if response.lower() != 'y':
                        print(f"跳过: {target_file_path}")
                        continue
                
                # 写入文件
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created: {target_file_path} (from {source_file_path})")
                
            except Exception as e:
                print(f"Error processing {source_file_path}: {e}")
    
    print("\n✅ 项目初始化完成!")
    return True


def main():
    CONFIG_DIRECTORY = Path(__file__).parent
    current_dir = os.getcwd()  # 当前工作目录
    config_dir = os.path.join(current_dir, 'config')
    
    os.makedirs(f"{config_dir}/yaml", exist_ok=True)
    create_config_files(
        template_files=
        {
            f"{config_dir}/yaml/search_config.yaml": os.path.join(CONFIG_DIRECTORY, "yaml/search_config_case.yaml"),
            f"{config_dir}/yaml/ollama_config.yaml": os.path.join(CONFIG_DIRECTORY, "yaml/ollama_config_qwen.yaml"),
            f"{config_dir}/yaml/sql_config.yaml": os.path.join(CONFIG_DIRECTORY, "yaml/sql_config_case.yaml"),
            f"{config_dir}/yaml/tool_config.yaml": os.path.join(CONFIG_DIRECTORY, "yaml/tool_config_case.yaml"),
            f"{current_dir}/.env": os.path.join(CONFIG_DIRECTORY, "yaml/.env"),
        },
    )


if __name__ == '__main__':
    main()