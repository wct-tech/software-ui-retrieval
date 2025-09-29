import os
import shutil

"""
    第0步（如果需要的话）
    将原文件夹中的图像 重命名为“General%Image_Cropping%07%1”的形式，并且统一输出到另一文件夹
    输出文件夹不包含场景等结构，只保证图像的名称唯一
    
    这个对原文件夹的要求是 有original/test等结构，original中图片名称应该是图片编号  如01.png
    test中图片名称是   图片编号_xxx_id  (xxx可有可无）
"""

data = []
image_folders = ["General", "System"]
output_folder = "F:/pycharm_project/general_evaluate_code/imgs/full_set_data"
# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

for folder in image_folders:
    folder_path = os.path.join("//imgs/latest_imgs", folder)
    sub_folders = os.listdir(folder_path)

    for sub_folder in sub_folders:
        # 操作original文件夹下图片，重命名为“场景%子场景%01（图片编号）%0（0代表是original原图）
        images_path_original = os.path.join(folder_path, sub_folder, "original")
        images_original = os.listdir(images_path_original)

        for image_original in images_original:
            img_name = os.path.splitext(image_original)[0]
            img_extension = os.path.splitext(image_original)[1]

            combined_name = f"{folder}%{sub_folder}%{img_name}%0"

            new_image_path = os.path.join(output_folder, combined_name + img_extension)
            old_image_path = os.path.join(images_path_original, image_original)
            # Copy the file to the output folder with the new name
            shutil.copy(old_image_path, new_image_path)
            print(f"Copied and renamed {old_image_path} to {new_image_path}")

        # 操作test文件夹下图片，重命名为“场景%子场景%01（图片编号）%1（1代表是测试图编号）
        images_path_test = os.path.join(folder_path, sub_folder, "test")
        images_test = os.listdir(images_path_test)

        for image_test in images_test:
            img_name = os.path.splitext(image_test)[0]
            img_extension = os.path.splitext(image_test)[1]

            combined_name = f"{folder}%{sub_folder}%{img_name.split('_')[0]}%{img_name.split('_')[-1]}"
            # print(combined_name)

            new_image_path = os.path.join(output_folder, combined_name + img_extension)
            old_image_path = os.path.join(images_path_test, image_test)
            # Copy the file to the output folder with the new name
            shutil.copy(old_image_path, new_image_path)
            print(f"Copied and renamed {old_image_path} to {new_image_path}")
