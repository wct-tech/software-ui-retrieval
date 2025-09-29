# software-ui-retrieval
## model_benchmark

#### **1.评测流程以及代码介绍**

**步骤一：生成评测集配置文件 config.json**

脚本地址：general_evaluate_code/code/imgs2json/imgs_config.py

运行该脚本生成配置文件，配置文件包括图片场景及相关case的信息，便于评测计算各个指标。

**步骤二：训练模型输出评测集对应向量，形成json格式**
需要使用训练后的模型，输出评测集图片对应的特征向量，形成json格式（包含图片名称和图片向量即可）

**步骤三：将模型json上传至es**

脚本地址：general_evaluate_code/code/es/upload_json.py

修改index_name（注意要全小写），图片向量的维度，以及模型json的地址，运行脚本即可将数据上传至 ES。

**步骤四：评测指标并生成报告**

脚本地址：general_evaluate_code/code/cal_metrics/main_metrics.py

修改index_name（和前面保持一致），模型名称，config.json的地址，以及k值。运行脚本，输出评测报告。

#### 2.其他代码说明

1.脚本地址：general_evaluate_code/code/es/search_delete_es.py

该脚本包含辅助管理函数：

* `check_data`：检查共有多少条数据。
* `delete_all_data`：删除 `index_name` 下的所有数据。

2.

* count_num.py：计算评测集图片数量

* img_blur.py： 图片随机模糊操作

* img_crop.py：图片随机裁切操作
3.私有评测数据样例
<img width="2880" height="1706" alt="General%Color_Loss%01%0" src="https://github.com/user-attachments/assets/dd398e29-7729-4fc4-addd-29d23dee351f" />
<img width="3840" height="1938" alt="General%Image_Blurring%04%5" src="https://github.com/user-attachments/assets/019a6437-375d-49fc-88e3-82b30174a2d9" />
<img width="2880" height="1706" alt="General%Image_Blurring%03%1" src="https://github.com/user-attachments/assets/c70ed68c-9991-4c22-97d6-faf7c692e17d" />
<img width="2880" height="1706" alt="General%Image_Blurring%01%0" src="https://github.com/user-attachments/assets/6d4c149e-99e8-4c19-9f95-cb859454ed50" />
<img width="1600" height="860" alt="General%Color_Loss%03%6" src="https://github.com/user-attachments/assets/4d123177-1655-4da4-b038-3e3abbf9b751" />


