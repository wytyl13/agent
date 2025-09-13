# Agent Framework

一个基于Python的智能Agent框架，支持多种LLM API、工具集成、数据库访问和检索增强生成功能。

## 项目描述

### 核心特性

- **多LLM支持**: 支持Ollama等多种大语言模型API接口
- **智能Agent系统**: 基于工具调用的规划Agent，支持复杂任务执行
- **工具生态**: 丰富的工具库，包括搜索、天气、数据库操作等
- **检索增强**: 支持向量检索和知识库增强生成
- **数据库集成**: 支持MySQL和PostgreSQL数据库操作
- **流式响应**: 支持实时流式输出，提升用户体验
- **配置驱动**: 灵活的YAML配置系统

### 架构概述

```
agent/
├── base/                 # 基础模块和抽象类
├── config/              # 配置管理模块
├── llm_api/             # 大语言模型API接口
├── models/              # 数据模型定义
├── provider/            # 数据提供者（数据库等）
├── retrieval_data/      # 检索数据存储
├── retrieval_storage/   # 检索索引存储
├── tool/                # 工具模块集合
└── utils/               # 工具函数
```

### 支持的功能

- **Agent类型**:
  - PlanningAgent: 规划执行Agent
  - DirectLLM: 直接LLM调用Agent
  - 自定义Tool Agent

- **工具集成**:
  - Google搜索
  - 天气API
  - 数据库操作
  - 文档检索
  - 水机设备API

- **数据库支持**:
  - MySQL
  - PostgreSQL

## pip一键安装（无法添加镜像源环境安装较慢）
```
pip install git+https://github.com/wytyl13/agent.git
```

## 下载源码并安装（支持镜像源安装较快，同时适合项目维护者和使用者）
### 1. 克隆项目

```bash
git clone https://github.com/wytyl13/agent.git
```

### 2. 环境安装

```bash
# 进入项目目录
cd agent

# 创建Python虚拟环境
conda create --name agent python=3.10
conda activate agent

# 安装依赖
pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 项目的维护者可以直接在源码根目录下进行开发维护

# 项目使用者在自己的项目中使用
mkdir /your_project && cd /your_project
# 初始化配置文件
agent init
```

```python
# 在/your_project目录下生成配置文件，修改即可
# 在自己的项目中使用示例 

from agent.tool.retrieval import Retrieval


if __name__ == '__main__':
    import asyncio
    retrieval = Retrieval(
        # data_dir="/work/ai/community_agent/retrieval_data",
        # index_dir="/work/ai/community_agent/retrieval_storage",
        chunk_size=256,
        chunk_overlap=20,
        line_based_chunk=False
    )

    async def main():
        result = await retrieval.execute(text_list=[], retrieval_word="test")
        print(result)
    asyncio.run(main())
```

### 3. 配置文件设置

#### SQL配置 (sql_config.yaml)

```yaml
host: postgres_20250811
port: 5433
username: your_username
password: your_password
database: postgres
table: sx_device_wavve_vital_sign_log
database_type: postgres
```

#### Ollama配置 (ollama_config.yaml)

```yaml
api_type: "ollama"
model: "qwen2.5:7b-instruct"
base_url: "http://192.168.0.17:11434/api"
```

#### Google搜索配置 (search_config.yaml)

```yaml
blocked_domains:
  - youtube.com
  - vimeo.com
  - dailymotion.com
  - bilibili.com
cx: "your_google_cx_id"
key: "your_google_api_key"
snippet_flag: true
query_num: 10
```

#### tool_config配置 (tool_config.yaml)

```yaml
class_name: # 工具类名称
    description: # 工具描述
    system_prompt: # 工具系统提示词
```


#### 环境变量配置，可以自定义路径 (.env)

```yaml
SEARCH_CONFIG_PATH=config/yaml/search_config.yaml
LLM_CONFIG_PATH=config/yaml/llm_config.yaml
SQL_CONFIG_PATH=config/yaml/sql_config.yaml
TOOL_CONFIG_PATH=config/yaml/tool_config.yaml
RETRIEVAL_DATA_PATH=retrieval_data
RETRIEVAL_STORAGE_PATH=retrieval_storage
API_PREFIX=https://ai.shunxikj.com:8890
MODEL_PATH=models
```


#### 知识库存放路径 (retrieval_data自动生成)

### 4. 配置路径

修改相关配置文件默认路径：
- `agent/config/yaml/sql_config.yaml`
- `agent/config/yaml/ollama_config_qwen.yaml`
- `agent/config/yaml/search_config.yaml`
- `agent/config/yaml/tool_config.yaml`

## 使用示例


###
```
以下示例为用户使用agent工具的调用方式
如果要对agent进行维护，在项目内使用相对路径表述
如：from agent.base.base_tool import tool
在项目维护时使用相对路径，具体取决于当前维护文件所在的路径：
    .base.base_tool import tool \ ..base.base_tool import tool \ ...base.base_tool import tool
```
### 1. 创建自定义Tool Agent

```python
from pydantic import Field, BaseModel
from typing import List, Optional, Dict, Type, Any
from agent.base.base_tool import tool
from agent.tool.enhance_retrieval import EnhanceRetrieval

class DirectLLMSchema(BaseModel):
    question: str = Field(
        ...,
        description="用户关于公司产品的完整问题,需根据当前问题和历史对话上下文进行综合理解和总结。"
    )

@tool
class DirectLLM:
    args_schema: Type[BaseModel] = DirectLLMSchema
    end_flag: int = 1  # 设置为1提高效率
    enhance_llm: Optional[EnhanceRetrieval] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'enhance_llm' in kwargs:
            self.enhance_llm = kwargs.pop('enhance_llm')
    
    async def execute(
        self, 
        question: str,
        message_history: List[Dict[str, Any]] = None,
        username: Optional[str] = None,
        location: Optional[str] = None,
        role: Optional[str] = None
    ):
        if self.enhance_llm:
            async for chunk in self.enhance_llm.execute(
                text_list=[],
                question=question,
                message_history=message_history,
                retrieval_flag=1,
                stream_flag=1
            ):
                yield chunk

# 使用示例
if __name__ == '__main__':
    from ..llm_api.ollama_llm import OllamaLLM
    from ..config.llm_config import LLMConfig
    from pathlib import Path
    import asyncio
    
    llm = OllamaLLM(
        config=LLMConfig.from_file(
            Path('/work/ai/agent/config/yaml/ollama_config_qwen.yaml')
        )
    )
    
    enhance_llm = EnhanceRetrieval(llm=llm)
    direct_llm = DirectLLM(enhance_llm=enhance_llm)
    
    async def main():
        async for chunk in direct_llm.execute(question="你是谁?"):
            print(chunk)
    
    asyncio.run(main())
```

### 2. 使用Ollama LLM API

```python
from agent.llm_api.ollama_llm import OllamaLLM
from agent.config.llm_config import LLMConfig
import asyncio

# 初始化LLM
ollama_llm = OllamaLLM(
    config=LLMConfig.from_file("/work/ai/agent/config/yaml/ollama_config_qwen.yaml")
)

async def main():
    # 流式调用
    async for chunk in ollama_llm._whoami_text_stream(
        messages=[{"role": "user", "content": "我是谁？"}],
        user_stop_words=[],
        timeout=10
    ):
        print(chunk, end='', flush=True)

if __name__ == '__main__':
    asyncio.run(main())
```

### 3. 使用数据库访问

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, BigInteger, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
import asyncio

from sqlalchemy.ext.declarative import declarative_base

# 创建统一的Base类
Base = declarative_base()

class CommunityRealTimeData(Base):
    """
    社区实时数据表 - 异步版本
    """
    __tablename__ = 'community_real_time_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    type = Column(String(32), nullable=True, comment='类型')
    content = Column(Text, nullable=True, comment='内容')
    url = Column(String(255), nullable=True, comment='链接地址')
    creator = Column(String(64), nullable=True, comment='创建人')
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='创建时间')
    updater = Column(String(64), nullable=True, comment='更新人')
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment='更新时间')
    tenant_id = Column(BigInteger, default=0, nullable=False, comment='租户编号')
    deleted = Column(SmallInteger, default=0, nullable=False, comment='是否删除')




from typing import TypeVar
from sqlalchemy.orm import sessionmaker
from ..provider.sql_provider import SqlProvider
from ..config.sql_config import SqlConfig

sql_provider = SqlProvider(model=CommunityRealTimeData, sql_config_path=self.sql_config_path)
result = sql_provider.get_record_by_condition(condition={}, fields=[])
```

### 4. 使用Planning Agent

```python
from agent.tool.planning_agent_community_ai_admin import PlanningAgentCommunityAiAdmin
from agent.tool.enhance_retrieval import EnhanceRetrieval
from agent.tool.direct_llm_community_ai_admin import DirectLLMCommunityAiAdmin
from agent.tool.weather_api import WeatherApi
import asyncio

# 初始化组件
enhance_llm = EnhanceRetrieval(retrieval_flag=False)
direct_llm_tool = DirectLLMCommunityAiAdmin(enhance_llm=enhance_llm)
weather_api = WeatherApi()

# 创建Planning Agent
planning_agent = PlanningAgentCommunityAiAdmin(
    tools=[direct_llm_tool, weather_api],
    enhance_llm=enhance_llm
)

async def main():
    async for chunk in planning_agent.execute(
        question="今天天气怎么样？",
        username="user123",
        location="北京",
        role="user"
    ):
        print(chunk, end='', flush=True)

if __name__ == '__main__':
    asyncio.run(main())
```

### 5. function_call使用示例
```
from .client_service import ClientService
from .order import Order
from .role import Role

QWEN_OLLAMA_CONFIG_PATH = "/work/ai/agent/config/yaml/ollama_config_qwen.yaml"
llm_qwen = OllamaLLM(config=LLMConfig.from_file(Path(QWEN_OLLAMA_CONFIG_PATH)))
DEFAULT_RETRIEVAL_DATA_PATH = "/work/ai/agent/retrieval_data"
DEFAULT_RETRIEVAL_STORAGE_PATH = "/work/ai/agent/retrieval_storage"
enhance_qwen_admin = EnhanceRetrieval(
    llm=llm_qwen, 
    retrieval_flag=False, 
    data_dir=DEFAULT_RETRIEVAL_DATA_PATH, 
    index_dir=DEFAULT_RETRIEVAL_STORAGE_PATH,
    embedding_model_path="/work/ai/agent/models"
)


client_service = ClientService()
order = Order()
role = Role()
tools = [client_service, order, role]
function_call = FunctionCall(
    tools = [client_service, order, role],
    enhance_llm=enhance_qwen_admin,
)


async def main():
    result = None
    history_message = None
    
    # function_call_case_1
    # tools = [client_service, order, role]
    # messages=[
    #     {"role": "user", "content": "帮我预定1份鸡蛋"},
    #     {"role": "assistant", "content": "好的，收到订单：鸡蛋 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
    #     {"role": "user", "content": "确认"},
    #     {"role": "assistant", "content": "好的，已经帮您预定鸡蛋 * 1"},
    #     {"role": "user", "content": "帮我预定1杯牛奶"},
    #     {"role": "assistant", "content": "好的，收到订单：牛奶 * 1。</text_value><confirm>请确认是否下单？</confirm>"},
    #     {"role": "user", "content": "取消"},
    #     {"role": "assistant", "content": "好的，没有为您下订单。如果您改变主意，请告诉我。"},
    # ]
    
    
    # function_call_case_2
    tools = [client_service, order, role]
    messages=[
        {"role": "user", "content": "我要新增一个角色"},
        {"role": "assistant", "content": "请提供具体的角色名称！"},
        {"role": "user", "content": "产品经理"},
        {"role": "assistant", "content": "请提供具体的权限！您可以从如下权限中选择：['服务项目管理', '商品分类管理', '设备类别管理']"},
        {"role": "user", "content": "服务项目和商品分类"},
        {"role": "assistant", "content": "<text_value>好的，收到新增：产品经理 * ['服务项目管理', '商品分类管理']。</text_value><confirm>请确认是否操作新增？</confirm>"},
    ]
    
    chunks = []
    async for chunk in function_call.execute(
        question="确认",
        messages=messages,
        tools=tools
    ):
        chunks.append(chunk)
    result = ''.join(chunks)
    print(result)
asyncio.run(main())
```




## 项目结构说明

- **base/**: 包含基础抽象类和装饰器
- **config/**: 配置文件管理和解析
- **llm_api/**: 各种LLM API的封装
- **tool/**: 各种功能工具的实现
- **provider/**: 数据提供者，如数据库连接
- **agent/**: Agent实现，如规划Agent

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 作者: weiyutao
- 项目链接: [https://github.com/wytyl13/agent](https://github.com/wytyl13/agent)