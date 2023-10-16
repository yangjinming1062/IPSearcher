import struct
from ipaddress import IPv4Address

from constants import Constants
from .classes import IP
from .classes import Singleton


class IPSearcher(metaclass=Singleton):
    # 整个读取xdb，保存在内存中
    _buff = None

    def __init__(self):
        with open(Constants.PATH_DB, 'rb') as f:
            self._buff = f.read()

    def search(self, ip):
        """
        检索IP信息。

        Args:
            ip (str | int | IPv4Address): 要搜索的IP地址。

        Returns:
            IP | None: 给定IP地址的信息，检索失败或不存在时返回None。

        Raises:
            ValueError: 如果IP地址既不是字符串也不是整数。
        """
        if isinstance(ip, str):
            ip = int(IPv4Address(ip))
        elif isinstance(ip, IPv4Address):
            ip = int(ip)
        assert isinstance(ip, int)
        return self._search(ip)

    def _search(self, ip):
        """
        根据给定的IP地址搜索区域信息。

        Args:
            ip (int): 整数格式的IP地址。

        Returns:
            IP | None: 给定IP地址的信息，检索失败或不存在时返回None。
        """
        # 基于矢量索引定位线段索引块
        il0 = (ip >> 24) & 0xFF
        il1 = (ip >> 16) & 0xFF
        idx = (il0 * Constants.VECTOR_INDEX_COLS * Constants.VECTOR_INDEX_SIZE) + (il1 * Constants.VECTOR_INDEX_SIZE)

        s_ptr = self._get_long(self._buff, Constants.HEADER_LENGTH + idx)
        e_ptr = self._get_long(self._buff, Constants.HEADER_LENGTH + idx + 4)

        # 二进制搜索段索引块以获取区域信息
        data_len = data_ptr = -1
        x = 0
        h = int((e_ptr - s_ptr) / Constants.SEGMENT_INDEX_SIZE)
        while x <= h:
            m = (x + h) >> 1
            p = s_ptr + (m * Constants.SEGMENT_INDEX_SIZE)
            # 读取段索引
            buffer_sip = self._read_buffer(p, Constants.SEGMENT_INDEX_SIZE)
            sip = self._get_long(buffer_sip, 0)
            if ip < sip:
                h = m - 1
            else:
                eip = self._get_long(buffer_sip, 4)
                if ip > eip:
                    x = m + 1
                else:
                    data_len = self._get_short(buffer_sip, 8)
                    data_ptr = self._get_long(buffer_sip, 10)
                    break

        # 没找到结果
        if data_ptr < 0:
            return None
        # 检索结果
        if buffer_string := self._read_buffer(data_ptr, data_len):
            return IP(ip, buffer_string.decode('utf-8'))

        return None

    def _read_buffer(self, offset, length):
        """
        检索算法用到的子函数，可以忽略。

        Args:
            offset (int): 要读取的部分的起始索引。
            length (int): 要读取的部分的长度。

        Returns:
            bytes: 由偏移量和长度指定的内容缓冲区部分。
        """
        if self._buff is None:
            self.__init__()
        return self._buff[offset:offset + length]

    @staticmethod
    def _get_long(b: bytes, offset: int) -> int:
        """
        检索算法用到的子函数，可以忽略。

        Args:
            b (bytes): 字节数组。
            offset (int): 字节数组中的偏移量。

        Returns:
            int: 长整数值。
        """
        if len(b[offset:offset + 4]) == 4:
            return struct.unpack('I', b[offset:offset + 4])[0]
        return 0

    @staticmethod
    def _get_short(b: bytes, offset: int) -> int:
        """
        检索算法用到的子函数，可以忽略。

        Args:
            b (bytes): 字节数组。
            offset (int): 字节数组中的偏移量。

        Returns:
            int: 2字节整数值。
        """
        return (b[offset] & 0x000000FF) | (b[offset + 1] & 0x0000FF00)
