"""
配置管理模块
使用pydantic-settings管理环境变量和配置
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # LLM配置
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4-turbo-preview', env='OPENAI_MODEL')
    openai_temperature: float = Field(default=0.7, env='OPENAI_TEMPERATURE')
    
    # Embedding配置
    embedding_model: str = Field(default='text-embedding-3-small', env='EMBEDDING_MODEL')
    
    # 向量数据库配置
    chroma_persist_directory: str = Field(default='./data/vectordb', env='CHROMA_PERSIST_DIRECTORY')
    
    # Redis配置
    redis_host: str = Field(default='localhost', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')
    redis_db: int = Field(default=0, env='REDIS_DB')
    
    # 应用设置
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    max_memory_messages: int = Field(default=50, env='MAX_MEMORY_MESSAGES')
    stream_enabled: bool = Field(default=True, env='STREAM_ENABLED')
    
    # 冰箱模式
    fridge_mode: str = Field(default='flexible', env='FRIDGE_MODE')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()
