import hashlib
import logging
import random
from time import sleep

import requests

APP_ID = '您的应用ID'
APP_KEY = '您的应用密钥'

URL = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def translate(query, from_lang='auto', to_lang='zh'):
    """
    将给定的查询从一种语言转换为另一种语言。

    Args:
        query (str): 要翻译的文本。
        from_lang (str, optional): 源文本的语言代码。默认为“auto”。
        to_lang (str, optional): 目标翻译的语言代码。默认为“zh”。

    Returns:
        str：翻译结果。
    """
    while True:
        salt = random.randint(32768, 65536)
        sign = hashlib.md5((APP_ID + query + str(salt) + APP_KEY).encode('utf-8')).hexdigest()

        payload = {
            'appid': APP_ID,
            'q': query,
            'from': from_lang,
            'to': to_lang,
            'salt': salt,
            'sign': sign
        }

        r = requests.post(URL, params=payload, headers=HEADERS)

        if r.ok:
            return r.json()['trans_result'][0]['dst']
        else:
            logging.warning(r.text)
            sleep(1)
