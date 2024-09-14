"""
The script is used to do background subtraction.
it loads calibrated images and corresponding semantic labels.
Then apply elementwise multiplication between images and labels,
the newly generated image has no background.
It can do the background subtraction for multiple subdatasets at the same time.
"""
from spectral import *
import numpy as np
import os
from PIL import Image
from hsi_calibration_utils import modify_hdr

IMG_PATH = ['E:\Sugarcane_Dataset_Normalized\sugarcane_22_Apr_2021_Norm',
            'E:\Sugarcane_Dataset_Normalized\sugarcane_15_Apr_2021_Norm',
            'E:\Sugarcane_Dataset_Normalized\sugarcane_8_Jun_2021_Norm',
            'E:\Sugarcane_Dataset_Normalized\sugarcane_23_Jun_2021_Norm']  # List of path of different subdatasets.
LABEL_PATH = ['E:\Sugarcane_Dataset_Label_V2\Apr22',
              'E:\Sugarcane_Dataset_Label_V2\Apr15',
              'E:\Sugarcane_Dataset_Label_V2\Jun8',
              'E:\Sugarcane_Dataset_Label_V2\Jun23']
SAVING_PATH = ['D:\Dataset\Apr22',
               # path for saving the newly generated image, these folders should be manually created.
               'D:\Dataset\Apr15',
               'D:\Dataset\Jun8',
               'D:\Dataset\Jun23']

# The subdataset folder should contain multiple subfolders.
for index in range(1, 4, 1):  # 4 subdatasets to be processed at a time, can edit the number.
    print(IMG_PATH[index])
    print(LABEL_PATH[index])
    print(SAVING_PATH[index])
    count = 0
    img_dir_list = []  # Save image sub-folders' name.
    img_file_list = []  # A list of list, each element is a list of images' name of a sub-folder.
    for (root, dirs, files) in os.walk(IMG_PATH[index], topdown=True):
        if len(dirs) != 0:
            img_dir_list = dirs
        if count > 0:
            li = []
            for i in files:
                if i.endswith('.hdr'):
                    li.append(i)
            img_file_list.append(li)
        count += 1

    label_dir_list = []
    label_file_list = []
    count = 0
    for (root, dirs, files) in os.walk(LABEL_PATH[index], topdown=True):
        if len(dirs) != 0:
            label_dir_list = dirs
        if count > 0:
            li = []
            for i in files:
                li.append(i)
            label_file_list.append(li)
        count += 1

    target_dirs = ["Q208_c", "Q208", "Q124_c", "Q124", "Q171_c",
                   "Q171", "Nco310", "Nco310_c", "Q205", "Q205_c",
                   "CP29-116", "CP29-116_c", "Q44", "Q44_c", "Q68",
                   "Q68_c", "Q78", "Q78_c", "Q82", "Q82_c"]

    for i in range(len(img_dir_list)):  # len(dir_list)
        # if img_dir_list[i] in target_dirs:
        if img_dir_list[i] in target_dirs:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(img_dir_list[i])
            for j in range(len(img_file_list[i])):  # len(file_list[i])
                os.chdir(IMG_PATH[index])
                img_path = img_dir_list[i] + "/" + img_file_list[i][j]
                print(img_path)
                img = envi.open(img_path)
                meta_data = img.metadata
                img = img[:, :, :]
                os.chdir(LABEL_PATH[index])
                label_path = label_dir_list[i] + "/" + label_file_list[i][j]
                print(label_path)
                label = np.array(Image.open(label_path, 'r'))[:, :, 0].astype(np.int32)
                label[label > 1] = 1
                label = np.reshape(label, (img.shape[0], img.shape[1], 1))
                new_img = np.multiply(img, label)
                os.chdir(SAVING_PATH[index])
                envi.save_image(img_dir_list[i] + "/" + img_file_list[i][j], new_img, dtype=np.float32,
                                metadata=meta_data, force=True, ext='.raw',
                                interleave='BSQ')
                modify_hdr(img_dir_list[i] + "/" + img_file_list[i][j])
                print("Finish setting background to zero")
