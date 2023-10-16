"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : classes.py
Author      : jinming.yang@qingteng.cn
Description : 工具类定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from ipaddress import IPv4Address


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IPSource:
    __slots__ = ('start', 'end', 'country_code', 'country', 'region', 'city', 'latitude', 'longitude')
    start: IPv4Address
    end: IPv4Address
    country_code: str
    country: str
    region: str
    city: str
    latitude: float
    longitude: float

    @classmethod
    def from_data(cls,
                  start_ip,
                  end_ip,
                  country_code,
                  country,
                  region,
                  city,
                  latitude,
                  longitude,
                  ):
        item = cls()
        item.start = IPv4Address(int(start_ip))
        item.end = IPv4Address(int(end_ip))
        item.country_code = country_code
        item.country = country
        item.region = region
        item.city = city
        item.latitude = float(latitude)
        item.longitude = float(longitude)
        return item


class IP:
    __slots__ = ('ip', 'country_code', 'country', 'region', 'city', 'latitude', 'longitude')

    def __init__(self, ip, source):
        """
        将searcher检索到的信息字符串转换为IP对象
        Args:
            ip (int): 检索的IP地址的int形式。
            source (str): searcher检索到的信息字符串。
        """
        tmp = source.split('|')  # 字符串结构取决于load_data函数写入时的数据处理
        self.ip = IPv4Address(ip)
        self.country_code = tmp[0]
        self.country = tmp[1]
        self.region = tmp[2]
        self.city = tmp[3]
        # self.latitude = tmp[4]
        # self.longitude = tmp[5]
