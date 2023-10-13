"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : config.py
Author      : jinming.yang
Description : 数据库连接信息等参数配置
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=('.env', 'dev.env'), env_file_encoding='utf-8', extra='ignore')
    # 默认IP
    host: str = Field('127.0.0.1', env='HOST')
    # 数据库相关参数
    db_host: str = host
    db_port: int = Field(5432)
    db_user: str = Field(alias='POSTGRESQL_USERNAME')
    db_pwd: str = Field(alias='POSTGRESQL_PASSWORD')
    db_db: str = Field(alias='POSTGRESQL_DATABASE')

    @property
    def db_uri(self):
        return f'postgresql+psycopg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_db}'
