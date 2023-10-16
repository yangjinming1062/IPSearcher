import hashlib
import time
import uuid

import requests

VOCAB_ID = None  # '您的用户词表ID'
APP_KEY = '您的应用ID'
APP_SECRET = '您的应用密钥'

URL = 'https://openapi.youdao.com/api'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def encrypt(sign_str):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(sign_str.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def translate(query, from_lang='auto', to_lang='zh-CHS'):
    """
    将给定的查询从一种语言转换为另一种语言。

    Args:
        query (str): 要翻译的文本。
        from_lang (str, optional): 源文本的语言代码。默认为“auto”。
        to_lang (str, optional): 目标翻译的语言代码。默认为“zh-CHS”。

    Returns:
        str：翻译结果。
    """
    while True:
        data = {
            'from': from_lang,
            'to': to_lang,
            'signType': 'v3',
            'appKey': APP_KEY,
            'q': query,
        }
        if VOCAB_ID:
            data['vocabId'] = VOCAB_ID
        current = str(int(time.time()))
        data['curtime'] = current
        salt = str(uuid.uuid1())
        sign_str = APP_KEY + truncate(query) + salt + current + APP_SECRET
        data['salt'] = salt
        data['sign'] = encrypt(sign_str)

        r = requests.post(URL, data=data, headers=HEADERS)
        if r.ok:
            return r.json()['translation'][0]
        else:
            time.sleep(1)
