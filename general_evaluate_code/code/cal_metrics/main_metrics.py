import numpy as np
import json
import os
from elasticsearch import Elasticsearch
import generate_report
import generate_report_with_img

"""
    第3步e
    评测指标并生成报告
"""

client = Elasticsearch(" ", basic_auth=(" ", " "))
index_name = " "  # 索引名称
model_name = " "  # 模型名称

# 从 config.json 读取配置
with open('general_evaluate_code/config_full_set_data1000.json', 'r') as f:
    config_data = json.load(f)

k = 5

# HTML报告路径
output_folder = f"general_evaluate_code/code/cal_metrics/report/{model_name}"  # 创建以模型名称命名的文件夹路径
os.makedirs(output_folder, exist_ok=True)
output_file_path = os.path.join(output_folder, f"report@{k}.html")


def get_image_vector(image_name):
    """
    从 Elasticsearch 中检索图像的特征向量
    """
    query = {
        "_source": ["image_vector"],
        "query": {
            "match_phrase": {"image_name": image_name}
        }
    }
    response = client.search(index=index_name, body=query)
    if response['hits']['hits']:
        return response['hits']['hits'][0]['_source']['image_vector']
    else:
        raise ValueError(f"No vector found for image {image_name}")


def compute_metrics(query_img, k, relevant_imgs):
    """
    计算单张图像的 Precision@k\ Recall@k\ AP@K \ topk accuracy
    query_img: 查询图像
    k: 计算前 k 个结果的精确度和准确度
    relevant_imgs: 该查询图像的相关图像集合
    """
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'image_vector') + 1.0",
                "params": {"query_vector": query_img['vector']}
            }
        }
    }

    response = client.search(index=index_name, body={
        "size": k + 1,  # 多检索一条记录，以防返回结果包含查询图像本身
        "query": script_query,
        "_source": {"includes": ["image_name", "image_vector"]}
    })
    hits = response['hits']['hits']
    retrieved_image_names = []
    retrieved_scores = []

    query_vector = query_img['vector']
    for hit in hits:
        if hit['_source']['image_vector'] == query_vector:
            continue  # 跳过查询图像本身
        retrieved_image_names.append(hit['_source']['image_name'])
        retrieved_scores.append(hit['_score'])
        if len(retrieved_image_names) >= k:
            break

    # 计算 topk accuracy
    correct = any(img in relevant_imgs for img in retrieved_image_names)
    accuracy = 1.0 if correct else 0.0

    # 计算 Precision@k
    relevant_count = sum(1 for img in retrieved_image_names if img in relevant_imgs)
    precision = relevant_count / k

    # 计算召回率
    recall = relevant_count / len(relevant_imgs)  # 除去图片本身

    # 计算AP（平均精度）
    retrieved_correct = 0
    p_sum = 0.0
    for i, img_name in enumerate(retrieved_image_names):
        if img_name in relevant_imgs:
            retrieved_correct += 1
            p_i = retrieved_correct / (i + 1)
            p_sum += p_i

    ap = p_sum / retrieved_correct if retrieved_correct != 0 else 0.0

    return accuracy, precision, recall, ap, retrieved_image_names, retrieved_scores


def compute_metrics_for_scene(scene, sub_scene, k):
    """
    计算特定场景的指标
    """
    accuracies = []
    precisions = []
    recalls = []
    APs = []

    images_info = []

    for scene_info in config_data:
        if scene_info['scene'] == scene and scene_info['sub_scene'] == sub_scene:
            for group in scene_info['imgs']:
                for img_name in group:
                    # 提取图像向量
                    img_vector = get_image_vector(img_name)
                    query_img = {'name': img_name, 'vector': img_vector}

                    del_self_relevant = [img for img in group if img != img_name]  # 相关图像 去掉检索图像自身
                    accuracy, precision, recall, ap, retrieved_image_names, retrieved_scores = compute_metrics(
                        query_img, k, del_self_relevant)

                    images_info.append({
                        'image_name': img_name,
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall,
                        'AP': ap,
                        'retrieved_images': retrieved_image_names,
                        'similarity_scores': retrieved_scores,
                        'correct_images': del_self_relevant
                    })

                    accuracies.append(accuracy)
                    precisions.append(precision)
                    recalls.append(recall)
                    APs.append(ap)
            break

    mean_accuracy = np.mean(accuracies) if accuracies else 0
    mean_precision = np.mean(precisions) if precisions else 0
    mean_recall = np.mean(recalls) if recalls else 0
    mean_ap = np.mean(APs) if APs else 0
    return mean_accuracy, mean_precision, mean_recall, mean_ap, images_info


if __name__ == '__main__':
    results = []

    scene_pairs = set((d['scene'], d['sub_scene']) for d in config_data)
    for scene, sub_scene in scene_pairs:
        mean_accuracy, mean_precision, mean_recall, mAP, images_info = compute_metrics_for_scene(scene, sub_scene, k)

        # 将所有的详细信息保存在一个列表中，以便生成HTML报告
        results.append({
            'scene': scene,
            'sub_scene': sub_scene,
            'mean_accuracy': mean_accuracy,  
            'mean_precision': mean_precision,
            'mean_recall': mean_recall,
            'mean_ap': mAP,
            'images_info': images_info
        })

    #生成HTML报告
    generate_report.generate_html_report(results, k, model_name, output_file=output_file_path)

    # # 生成显示图片的HTML报告
    # generate_report_with_img.generate_html_report(results, k, model_name, output_file=output_file_path,
    #                                               images_path=r"D:\Haojing\data\test\full_set_data")
