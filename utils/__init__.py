"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在init中导入各个子文件中的类、方法就可以直接从utils导入而无需关心具体路径了
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import sys

from loguru import logger

from .classes import DatabaseManager
from .classes import Singleton
from .functions import exceptions
from .functions import generate_key

# 日志记录
logger.add(sys.stdout, colorize=True, format='{time:YYYY-MM-DD HH:mm:ss}|<level>{message}</level>')
