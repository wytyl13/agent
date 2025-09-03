from typing import Dict, Optional, Union, Any
from pathlib import Path
import os
from dotenv import load_dotenv

from ..utils.yaml_model import YamlModel
from ..utils.utils import Utils

utils = Utils()

ROOT_DIRECTORY = Path(__file__).parent.parent
TOOL_CONFIG_PATH = str(ROOT_DIRECTORY / "config" / "yaml" / "tool_config.yaml")


environment = utils.load_project_env()
# TOOL_CONFIG_PATH = environment["TOOL_CONFIG_PATH"] if "TOOL_CONFIG_PATH" in environment else TOOL_CONFIG_PATH


class ToolConfigLoader(YamlModel):
    """工具配置加载器，用于加载特定工具的配置"""
    
    
    @classmethod
    def _merge_dicts(cls, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """简单的字典合并"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    
    @classmethod
    def get_tool_config(cls, tool_name: str, config_path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
        """
        获取特定工具的配置
        
        Args:
            tool_name: 工具名称（类名）
            config_path: 配置文件路径，如果为None，则使用默认路径
            
        Returns:
            工具配置字典，如果不存在则返回空字典
        """
        if config_path is not None:
            # 使用指定配置路径
            all_configs = cls.read(config_path)
            if isinstance(all_configs, dict):
                return all_configs.get(tool_name, {})
            return {}
        
        # 加载默认配置
        default_config = {}
        if os.path.exists(TOOL_CONFIG_PATH):
            try:
                default_all = cls.read(TOOL_CONFIG_PATH)
                if isinstance(default_all, dict):
                    default_config = default_all.get(tool_name, {})
            except:
                pass
        
        # 加载用户配置
        user_config = {}
        user_config_path = environment.get('TOOL_CONFIG_PATH') or os.environ.get('WHOAMI_TOOL_CONFIG_PATH')
        if user_config_path and os.path.exists(user_config_path):
            try:
                user_all = cls.read(user_config_path)
                if isinstance(user_all, dict):
                    user_config = user_all.get(tool_name, {})
            except:
                pass
        
        # 合并配置：用户配置覆盖默认配置
        if default_config and user_config:
            return cls._merge_dicts(default_config, user_config)
        elif user_config:
            return user_config
        else:
            return default_config
    
    
if __name__ == '__main__':
    print(TOOL_CONFIG_PATH)
    