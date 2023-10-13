"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : base.py
Author      : jinming.yang
Description : model基础信息定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.properties import ColumnProperty
from typing_extensions import Annotated

from config import Configuration

CONFIG = Configuration()

str_id = Annotated[str, mapped_column(String(16))]
str_small = Annotated[str, mapped_column(String(32))]
str_medium = Annotated[str, mapped_column(String(64))]
str_large = Annotated[str, mapped_column(String(128))]


class ModelBase(DeclarativeBase):
    """
    提供公共方法的基类
    """

    @classmethod
    def get_columns(cls):
        """
        获取类中的全部数据库列的名称。

        Returns:
            列名称列表
        """
        return [p.key for p in cls.__mapper__.iterate_properties if isinstance(p, ColumnProperty)]

    @classmethod
    def get_properties(cls):
        """
        获取类中的全部数据库列。

        Returns:
            列名称列表
        """
        return [p for p in cls.__mapper__.iterate_properties if isinstance(p, ColumnProperty)]

    @classmethod
    def to_property(cls, *name):
        """
        根据列名获取对应的列

        Args:
            name (str): 列名。
        """
        return getattr(cls, name[0]) if len(name) == 1 else [getattr(cls, x) for x in name]

    def json(self, excluded=None) -> dict:
        """
        将ORM实例转换为可序列化字典。

        Args:
            excluded (set | None): 要从结果中排除的列名。

        Returns:
            dict: 序列化结果。
        """
        result = {}
        ignored_fields = excluded or set()

        # 遍历ORM实例的属性
        for prop in self.__mapper__.iterate_properties:
            # 跳过非列的属性
            if not isinstance(prop, ColumnProperty):
                continue
            # 跳过以“_”开头或位于ignored_fields集中的属性
            if prop.key.startswith('_') or prop.key in ignored_fields:
                continue
            value = getattr(self, prop.key)
            # 如果该值是ORM实例的列表，则对每个项递归调用json（）方法
            if isinstance(value, InstrumentedList):
                result[prop.key] = [item.json() for item in value]
            # 如果该值是另一个ORM实例，则递归调用json（）方法
            elif isinstance(value, ModelBase):
                result[prop.key] = value.json()
            # 如果列类型为JSON，则直接返回json内容
            elif isinstance(prop.columns[0].type, JSON):
                result[prop.key] = value if value else None
            # 如果列类型为DateTime，当日期为空时返回'-'字符串
            elif isinstance(prop.columns[0].type, DateTime):
                result[prop.key] = value if value else '-'
            else:
                result[prop.key] = value

        return result
