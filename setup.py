from setuptools import setup, find_packages

setup(
    name="agent",  # 你的包名
    version="0.1.0",
    
    packages=['agent'] + ['agent.' + pkg for pkg in find_packages()],
    package_dir={'agent': '.'},  # agent包就是当前目录
    package_data={
        'agent.config': ['yaml/*.yaml', 'yaml/.env'],
    },
    include_package_data=True,
    install_requires=[
        "aiomysql",
        "asyncpg", 
        "readability-lxml",
        "trafilatura",
        "bs4",
        "newspaper3k",
        "gne",
        "colorlog",
        "aiohttp",
        "openai",
        "simhash",
        "pydantic",
        "PyYAML",
        "sqlalchemy",
        "mysql-connector-python",
        "numpy==1.26.4",
        "matplotlib",
        "nest-asyncio",
        "pytest-asyncio",
        "pytest",
        "python-docx",
        "llama-index-embeddings-huggingface",
        "llama-index-readers-file",
        "llama-index-retrievers-bm25",
        "huggingface-hub",
        "alibabacloud_iqs20240712",
        "pypdf",
        "rank-bm25",
        "jieba",
        "psutil",
        "dotenv",
        "rich",
        "modelscope",
        "torchaudio>=2.6.0"
    ],
    
    # 添加命令行工具
    entry_points={
    'console_scripts': [
        'agent=agent.config.init_yaml:main',  # 指向包的入口
    ],
},
)
