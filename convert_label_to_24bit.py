"""
This script is used to convert 32 bit depth rgb label to 24 bit depth label.
We used Windows Paint to improve our semantic labels for sugarcane images,
Windows Paint saves label as 32 bit depth file, in that case labels will have 4 channels.
So we need to convert the label into 3 channels label.

Parameters need change:
1) path
2) dir_li
3) img_li
"""

import os
from PIL import Image
import numpy as np


def convertion_32_to_24(img, img_name):
    """
    @param img: image as in numpy array
    @param img_name: image name
    """
    a = img[:, :, 0]
    print(np.unique(a))
    new_label = np.zeros((a.shape[0], a.shape[1], 3))
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            if a[i][j] == 255:
                new_label[i][j][0] = 128
    # new_label=np.concatenate((np.reshape(img[:,:,0],(1088,2048,1)),np.reshape(img[:,:,1],(1088,2048,1)),np.reshape(img[:,:,3],(1088,2048,1))),axis=2)
    print(new_label.shape)
    rescale_im = (255.0 / new_label.max() * (new_label - new_label.min())).astype(np.uint8)
    im2 = Image.fromarray(rescale_im)
    im2.save(img_name)


path = "E:/Sugarcane_Dataset_Label/Sep1"  # Path of the subdataset folder, replaced it with yours.
dir_li = ["Q171", "Q171_c", "Q205_c", "Q208_c"]  # Target directory path.
img_li = ["Q171_4_normalized.png", "Q171_10_normalized.png", "Q171_6_c_normalized.png",
          "Q205_4_c_normalized.png", "Q208_5_c_normalized.png", ]  # Target images.
for dir in dir_li:
    imgs = os.listdir(path + "/" + dir)
    print(path + "/" + dir)
    os.chdir(path + "/" + dir)
    for item in imgs:
        if item in img_li:
            img = np.array(Image.open(item, 'r')).astype(np.uint8)
            convertion_32_to_24(img, item)
