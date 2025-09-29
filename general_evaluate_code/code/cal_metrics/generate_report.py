"""生成简单的html报告，不显示图片"""

from jinja2 import Template


def calculate_global_metrics(results):
    global_mean_accuracy = 0
    global_mean_precision = 0
    global_mean_recall = 0
    global_mean_ap = 0
    count = 0

    for result in results:
        global_mean_accuracy += result['mean_accuracy']
        global_mean_precision += result['mean_precision']
        global_mean_recall += result['mean_recall']
        global_mean_ap += result['mean_ap']
        count += 1

    # 计算平均值
    if count > 0:
        global_mean_accuracy /= count
        global_mean_precision /= count
        global_mean_recall /= count
        global_mean_ap /= count

    return global_mean_accuracy, global_mean_precision, global_mean_recall, global_mean_ap


def generate_html_report(results, k, model_name, output_file):
    """
    根据结果生成 HTML 报告
    """
    # 计算全局指标
    global_mean_accuracy, global_mean_precision, global_mean_recall, global_mean_ap = calculate_global_metrics(results)

    template = Template("""  
        <!DOCTYPE html>  
        <html lang="en">  
        <head>  
            <meta charset="UTF-8">  
            <title>评测报告</title>  
            <style>  
                body { font-family: Arial, sans-serif; }  
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }  
                th, td { border: 1px solid #000; padding: 8px; text-align: left; }  
                th { background-color: #f2f2f2; }  
                h2, h1 { background-color: #f8f8f8; padding: 10px; }  
            </style>  
        </head>  
        <body>  
            <h1>评价指标@{{ k }} 报告 模型: {{ model_name }}</h1>  

            <div class="global-metrics">  
                <h2>全局指标</h2>  
                <p> top-{{ k }} accuracy: {{ global_mean_accuracy }}</p>  
                <p> mean- Precision@{{ k }}: {{ global_mean_precision }}</p>  
                <p> mean- Recall@{{ k }}: {{ global_mean_recall }}</p>  
                <p> mean- AP@{{ k }}: {{ global_mean_ap }}</p>  
            </div>
             
            {% for result in results %}  
            <h2>{{ result.scene }} / {{ result.sub_scene }}</h2>  
            <p>top-{{ k }} accuracy: {{ result.mean_accuracy }}</p>  
            <p>mean- Precision@{{ k }}: {{ result.mean_precision }}</p>  
            <p>mean- Recall@{{ k }}: {{ result.mean_recall }}</p>  
            <p>mean- AP@{{ k }}: {{ result.mean_ap }}</p>  
            <table>  
                <tr>  
                    <th>Image</th>  
                    <th>Accuracy</th>  
                    <th>Precision</th>  
                    <th>Recall</th>  
                    <th>AP</th>  
                    <th>Retrieved Images</th>  
                    <th>Similarity Scores</th>  
                    <th>Correct Images</th>  
                </tr>  
                {% for image_info in result.images_info %}  
                <tr>  
                    <td>{{ image_info.image_name }}</td>  
                    <td>{{ image_info.accuracy }}</td>  
                    <td>{{ image_info.precision }}</td>  
                    <td>{{ image_info.recall }}</td>  
                    <td>{{ image_info.AP }}</td>  
                    <td>  
                        <ul>  
                        {% for img in image_info.retrieved_images %}  
                            <li>{{ img }}</li>  
                        {% endfor %}  
                        </ul>  
                    </td>  
                    <td>  
                        <ul>  
                        {% for score in image_info.similarity_scores %}  
                            <li>{{ score - 1 }}</li>  
                        {% endfor %}  
                        </ul>  
                    </td>  
                    <td>  
                        <ul>  
                        {% for correct_img in image_info.correct_images %}  
                            <li>{{ correct_img }}</li>  
                        {% endfor %}  
                        </ul>  
                    </td>  
                </tr>  
                {% endfor %}  
            </table>  
            {% endfor %}  
        </body>  
        </html>  
    """)

    html_content = template.render(
        results=results, k=k, model_name=model_name,
        global_mean_accuracy=global_mean_accuracy,
        global_mean_precision=global_mean_precision,
        global_mean_recall=global_mean_recall,
        global_mean_ap=global_mean_ap
    )
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)