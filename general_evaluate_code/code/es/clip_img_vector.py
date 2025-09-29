import base64
import json
import os
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers




host_url = ''      # clip模型地址
imgs_folder = ""  # 全库数据

ELASTIC_HOSTS = ""    # es地址
ELASTIC_USER = ""    # 用户名
ELASTIC_PASSWORD = ""   # es密码

index_name = "cn_clip_cub200"

def query_img_vector(image_path):
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    payload = {
        "image": image_data
    }

    r = requests.post(url=host_url, json=payload)

    if r.status_code == 200:
        image_vector = json.loads(r.text)
        return image_vector
    else:
        print('query image vector failed, image:{}, response: {}.'.format(image_path, r.text))
        return None


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
                        "dims": 768,    # 更改维度
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
    for img in os.listdir(imgs_folder):
        img_path = os.path.join(imgs_folder, img)

        # 使用 CLIP 模型提取特征向量
        image_vector = query_img_vector(img_path)

        if img_path is not None:
            img_datas.append({
                "image_name": img,
                "image_vector": image_vector
            })

        else:
            print(f"Failed to extract feature vector for image: {img_path}")

    add_data(client, img_datas, index_name)

