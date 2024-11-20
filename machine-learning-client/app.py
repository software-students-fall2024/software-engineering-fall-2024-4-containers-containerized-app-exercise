from pymongo import MongoClient
import numpy as np
import time

def collect_and_analyze_data():
    # 连接到 MongoDB 数据库
    client = MongoClient("mongodb://mongodb:27017/")
    db = client.ml_data
    collection = db.results

    # 模拟数据收集和分析
    while True:
        data = {"values": list(np.random.rand(5))}
        collection.insert_one(data)
        print("Data inserted:", data)
        time.sleep(10)  # 每 10 秒插入一次数据

if __name__ == "__main__":
    collect_and_analyze_data()
