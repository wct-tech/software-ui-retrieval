import json
import os
from collections import defaultdict


"""
    第1步
    在全库测试数据中，根据其唯一名称，将命名模式分解并统计成一个 JSON 文件
"""

imgs_folder = "./flowers"
json_name = './general_evaluate_code/config_full_set_data1000.json'


# 构建一个嵌套字典，用于组织结构化数据
data_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

# 遍历文件名，解析并填充到字典中
for filename in os.listdir(imgs_folder):
    scene, sub_scene, group, idx = filename.split('%')
    data_dict[scene][sub_scene][group].append(filename)

# 将数据结构转换为列表形式，以匹配目标 JSON 结构
final_list = []
for scene, sub_scenes in data_dict.items():
    for sub_scene, groups in sub_scenes.items():
        entry = {
            "scene": scene,
            "sub_scene": sub_scene,
            "imgs": list(groups.values())
        }
        final_list.append(entry)

# 转换为 JSON 格式并保存到文件
json_output = json.dumps(final_list, indent=4, ensure_ascii=False)
with open(json_name, 'w', encoding='utf-8') as f:
    f.write(json_output)

print("JSON 文件已生成：", json_name)