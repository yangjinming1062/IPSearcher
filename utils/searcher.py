import ipaddress
import json
import os
from mmap import mmap
from struct import unpack
from zipfile import ZipFile

from constants import Constants
from .classes import IP
from .classes import Singleton


class IPSearcher(metaclass=Singleton):
    """
    IP数据检索
    """

    def __init__(self):
        if not os.path.isfile(Constants.PATH_DB):
            zip_path = f'{Constants.PATH_DB}.zip'
            if not os.path.exists(zip_path):
                raise ValueError('数据库文件似乎不存在。')
            else:
                with ZipFile(zip_path, 'r') as zip_ref:
                    name = os.path.basename(Constants.PATH_DB)
                    target = os.path.dirname(Constants.PATH_DB)
                    zip_ref.extract(name, target)
        with open(Constants.PATH_DB, 'r+b') as db:
            self.db = mmap(db.fileno(), 0)
        # 加载BIN文件头信息
        header_row = self.db[0:32]
        self._db_type = unpack('B', header_row[0:1])[0]
        self._db_column = unpack('B', header_row[1:2])[0]
        self._v4_count = unpack('<I', header_row[5:9])[0]
        self._v4_addr = unpack('<I', header_row[9:13])[0]
        self._v6_count = unpack('<I', header_row[13:17])[0]
        self._v6_addr = unpack('<I', header_row[17:21])[0]
        self._v4_base_addr = unpack('<I', header_row[21:25])[0]
        self._v6_base_addr = unpack('<I', header_row[25:29])[0]

        # 加载国家翻译记录
        if os.path.exists(Constants.PATH_COUNTRY):
            with open(Constants.PATH_COUNTRY, 'r', encoding='utf-8') as f:
                self.translate_country = json.load(f)
        else:
            self.translate_country = {'-': '-'}
        # 加载区域翻译记录
        if os.path.exists(Constants.PATH_REGION):
            with open(Constants.PATH_REGION, 'r', encoding='utf-8') as f:
                self.translate_region = json.load(f)
        else:
            self.translate_region = {'-': '-'}
        # 加载城市翻译记录
        if os.path.exists(Constants.PATH_CITY):
            with open(Constants.PATH_CITY, 'r', encoding='utf-8') as f:
                self.translate_city = json.load(f)
        else:
            self.translate_city = {'-': '内网IP'}

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    def _read_str(self, offset):
        self.db.seek(offset - 1)
        data = self.db.read(257)
        char_count = unpack('B', data[0:1])[0]
        string = data[1:char_count + 1]
        return string.decode('iso-8859-1')

    def _read_int(self, offset):
        self.db.seek(offset - 1)
        return unpack('<L', self.db.read(4))[0]

    def _read_info(self, ip, mid, ip_version):
        info = IP()
        info.ip = ip

        if ip_version == 4:
            off = 0
            base_addr = self._v4_addr
            column_width = self._db_column * 4 + 4
        else:
            off = 12
            base_addr = self._v6_addr
            column_width = self._db_column * 4

        def calc_off(position, mid):
            return base_addr + mid * (self._db_column * 4 + off) + off + 4 * position

        raw_start = (calc_off(Constants.INDEX_COUNTRY, mid)) - 1
        raw = self.db[raw_start: raw_start + column_width]

        # 国家信息
        country_end = (Constants.INDEX_COUNTRY * 4)
        country_code = self._read_str(unpack('<I', raw[0: country_end])[0] + 1)
        country = self._read_str(unpack('<I', raw[0: country_end])[0] + 4)
        if country_code in ('CN', 'HK', 'MO', 'TW'):
            info.country_code = 'CN'
            info.country = '中国'
        else:
            info.country_code = country_code
            info.country = self.translate_country.get(country, country)
        # 区域信息
        region_end = (Constants.INDEX_REGION * 4)
        region = self._read_str(unpack('<I', raw[region_end - 4: region_end])[0] + 1)
        if country_code == 'TW':
            info.region = '台湾'
        else:
            info.region = self.translate_region.get(region, region)
        # 城市信息
        city_end = (Constants.INDEX_CITY * 4)
        city = self._read_str(unpack('<I', raw[city_end - 4: city_end])[0] + 1)
        if country_code == 'HK':
            # 香港数据精细到了街道，这里直接统一香港
            info.city = '香港'
        else:
            info.city = self.translate_city.get(city, city)
        # 经纬度信息
        if self._db_type >= 5:
            latitude_end = (Constants.INDEX_LATITUDE * 4)
            latitude = round(unpack('<f', raw[latitude_end - 4: latitude_end])[0], 6)
            info.latitude = float(format(latitude, '.6f'))
            longitude_end = (Constants.INDEX_LONGITUDE * 4)
            longitude = round(unpack('<f', raw[longitude_end - 4: longitude_end])[0], 6)
            info.longitude = float(format(longitude, '.6f'))
        return info

    def _read_32x2(self, offset):
        self.db.seek(offset - 1)
        data = self.db.read(8)
        return unpack('<L', data[0:4])[0], unpack('<L', data[4:8])[0]

    def _read_row32(self, offset):
        data_length = self._db_column * 4 + 4
        self.db.seek(offset - 1)
        raw_data = self.db.read(data_length)
        ip_start = unpack('<L', raw_data[0:4])[0]
        ip_end = unpack('<L', raw_data[data_length - 4:data_length])[0]
        return ip_start, ip_end

    def _read_row128(self, offset):
        data_length = self._db_column * 4 + 12 + 16
        self.db.seek(offset - 1)
        raw_data = self.db.read(data_length)
        return ((unpack('<L', raw_data[12:16])[0] << 96) | (unpack('<L', raw_data[8:12])[0] << 64) | (
                unpack('<L', raw_data[4:8])[0] << 32) | unpack('<L', raw_data[0:4])[0],
                (unpack('<L', raw_data[data_length - 4:data_length])[0] << 96) | (
                        unpack('<L', raw_data[data_length - 8:data_length - 4])[0] << 64) | (
                        unpack('<L', raw_data[data_length - 12:data_length - 8])[0] << 32) |
                unpack('<L', raw_data[data_length - 16:data_length - 12])[0])

    def search(self, address):
        """
        检索IP信息。

        Args:
            address (int | str | bytes | IPv4Address | IPv6Address): 要搜索的IP地址。

        Returns:
            IP | None: 给定IP地址的信息，检索失败或不存在时返回None。

        Raises:
            ValueError: 待检索的信息不是有效IP。
        """
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv4Address):
            ip_version = 4
            ip_number = int(ip)
            base_addr = self._v4_addr
            index = ((ip_number >> 16) << 3) + self._v4_base_addr
            low, high = self._read_32x2(index)
        else:
            ip_version = 6
            ip_number = int(ip)
            base_addr = self._v6_addr
            index = ((ip_number >> 112) << 3) + self._v6_base_addr
            low = self._read_int(index)
            high = self._read_int(index + 4)

        while low <= high:
            mid = int((low + high) / 2)
            if ip_version == 4:
                ip_start, ip_end = self._read_row32(base_addr + mid * self._db_column * 4)
            else:
                ip_start, ip_end = self._read_row128(base_addr + mid * ((self._db_column * 4) + 12))

            if ip_start <= ip_number < ip_end:
                return self._read_info(ip, mid, ip_version)
            else:
                if ip_number < ip_start:
                    high = mid - 1
                else:
                    low = mid + 1
