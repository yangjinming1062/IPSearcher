import csv

from models import *
from utils import *


def load_data():
    batch_size = 100000
    with DatabaseManager() as db:
        batch_list = []
        files = {
            './data/IP2LOCATION-LITE-DB5.CSV': 4,
            './data/IP2LOCATION-LITE-DB5.IPV6.CSV': 6,
        }
        logger.info(f'开始加载数据...')
        total = 0
        for path, version in files.items():
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    item = IPLocation.from_data(version, *row)
                    item.id = generate_key(version, item.start, item.end)
                    batch_list.append(item)
                    if len(batch_list) >= batch_size:
                        total += len(batch_list)
                        db.add_all(batch_list)
                        db.commit()
                        logger.info(f'累计写入{total}条')
                        batch_list.clear()
                if batch_list:
                    db.add_all(batch_list)
                    db.commit()
        logger.info(f'数据加载完成')


if __name__ == '__main__':
    load_data()
