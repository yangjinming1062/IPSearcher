"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : loader.py
Author      : jinming.yang
Description : 基础方法的定义实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import csv
import json
import os

from tqdm import tqdm

from constants import Constants
from translation.baidu import translate
from utils import logger
from .classes import IPSource


def load_data():
    # 加载国家翻译记录
    if os.path.exists(Constants.PATH_COUNTRY):
        with open(Constants.PATH_COUNTRY, 'r', encoding='utf-8') as f:
            country_translate_dict = json.load(f)
    else:
        country_translate_dict = {'-': '-'}
    # 加载区域翻译记录
    if os.path.exists(Constants.PATH_REGION):
        with open(Constants.PATH_REGION, 'r', encoding='utf-8') as f:
            region_translate_dict = json.load(f)
    else:
        region_translate_dict = {'-': '-'}
    # 加载城市翻译记录
    if os.path.exists(Constants.PATH_CITY):
        with open(Constants.PATH_CITY, 'r', encoding='utf-8') as f:
            city_translate_dict = json.load(f)
    else:
        city_translate_dict = {'-': '内网IP'}
    # 加载的原始CSV文件
    ip_data = []
    # 数据文件过大，请通过https://lite.ip2location.com/database-download下载csv数据后放到当前目录进行数据加载
    with open(Constants.PATH_SOURCE, 'r', encoding='utf-8') as f:
        logger.info(f'数据开始加载')
        reader = csv.reader(f)
        for row in reader:
            ip_data.append(IPSource.from_data(*row))
        logger.info(f'数据加载完成，总数据量：{len(ip_data)}')
    # 防止单次请求因意外原因中断，可以接续完成后续数据的写入（翻译接口是有限额的）
    try:
        with open(Constants.PATH_TARGET, 'w+', encoding='utf-8') as f:
            start_index = len(f.readlines())
            end_index = len(ip_data) - 1
            logger.info(f'开始数据转换')
            translated_data = []
            for index in tqdm(range(start_index, end_index)):
                item: IPSource = ip_data[index]
                tmp = [str(item.start), str(item.end), item.country_code]
                # 国家信息
                if item.country not in country_translate_dict:
                    country_translate_dict[item.country] = translate(item.country)
                tmp.append(country_translate_dict.get(item.country, item.country))
                # 区域信息
                if item.region not in region_translate_dict:
                    region_translate_dict[item.region] = translate(item.region)
                tmp.append(region_translate_dict.get(item.region, item.region))
                # 城市信息
                if item.city not in city_translate_dict:
                    city_translate_dict[item.city] = translate(item.city)
                tmp.append(city_translate_dict.get(item.city, item.city))
                # 经纬度
                # tmp.append(row.latitude)
                # tmp.append(row.longitude)
                translated_data.append('|'.join(tmp))
            logger.info(f'数据转换完成')
    except Exception as ex:
        logger.exception(ex)
        logger.info(f'当前: {start_index=}')
    finally:
        # 避免每次变更都写数据拖慢处理进度
        json.dump(country_translate_dict, open(Constants.PATH_COUNTRY, 'w'), indent=4, ensure_ascii=False)
        json.dump(region_translate_dict, open(Constants.PATH_REGION, 'w'), indent=4, ensure_ascii=False)
        json.dump(city_translate_dict, open(Constants.PATH_CITY, 'w'), indent=4, ensure_ascii=False)
