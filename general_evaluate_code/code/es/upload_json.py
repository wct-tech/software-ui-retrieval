import base64
import json
import os
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers

"""
    第2步 
    （model_json下的模型json文件包括）全库数据的图片特征向量，将数据直接上传到es中，只包括名称和特征向量(记得改图片向量的维度)
"""

imgs_folder = " " # 全库数据

ELASTIC_HOSTS = " "    # es地址
ELASTIC_USER = " "    # 用户名
ELASTIC_PASSWORD = " "   # es密码

index_name = " "    # 注意要全小写


def check_data_exist(client, index_name, data):
    """检查该数据在es中是否存在"""
    query = {
        "bool": {
            "must": [
                {"match_phrase": {"image_name": data["image_name"]}}
            ]
        }
    }

    res = client.search(index=index_name, body={"query": query})

    if res["hits"]["total"]["value"] > 0:
        print("Data already exists")
        return True  # Data already exists
    else:
        return False  # Data does not exist


def add_data(client, img_datas, index_name):
    # Create index if it does not exist
    if not client.indices.exists(index=index_name):
        mappings = {
            "mappings": {
                "properties": {
                    "image_vector": {
                        "type": "dense_vector",
                        "dims":  768,  # 更改维度
                        "similarity": "cosine"
                    },
                    "image_name": {
                        "type": "text"
                    }
                }
            }
        }
        client.indices.create(index=index_name, body=mappings)

    success_count = 0
    failed_count = 0
    for item in img_datas:
        # Check if data already exists
        if not check_data_exist(client, index_name, item):
            # Prepare the action for inserting the data
            action = {
                "_index": index_name,
                "_source": {
                    "image_name": item["image_name"],
                    "image_vector": item["image_vector"]
                }
            }
            # Execute the insert action
            success, failed = helpers.bulk(client, [action], refresh=True, stats_only=True)
            success_count += success
            failed_count += failed

    # Print total operations count
    print(f"Total successful operations: {success_count}, Total failed operations: {failed_count}")


if __name__ == '__main__':
    # Create Elasticsearch client
    client = Elasticsearch(ELASTIC_HOSTS, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))

    # List image files and process them
    img_datas = []

    with open("/general_evaluate_code/model_json/config_full_set_data1000.json", 'r') as file:
        data = file.read()

    # 解析 JSON 内容
    img_datas = json.loads(data)

    add_data(client, img_datas, index_name)
