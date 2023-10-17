"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : classes.py
Author      : jinming.yang@qingteng.cn
Description : 工具类定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from ipaddress import IPv4Address
from ipaddress import IPv6Address


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IP:
    __slots__ = ('ip', 'country_code', 'country', 'region', 'city', 'latitude', 'longitude')
    ip: IPv4Address | IPv6Address
    country_code: str
    country: str
    region: str
    city: str
    latitude: float
    longitude: float
