"""
This script is used to convert all the hsi image of a given subdataset into rgb images.

Parameters need change:
1) IMG_PATH Make sure to manually create a RGB folder under this IMG_PATH
"""
from spectral import *
import numpy as np
import os
from PIL import Image


def hsi2rgb_conversion(hsi_img, save_path):
    """
    @param hsi_img: hyperspectral image as in numpy array
    @param save_path: path to save generated rgb image.
    """
    bl = hsi_img[:, :, 8]  # Select a random band from red, green and blue wavelength range.
    gr = hsi_img[:, :, 25]
    re = hsi_img[:, :, 70]
    my_rgb = np.dstack((np.dstack((re, gr)), bl))
    my_rgb = np.double(np.double(my_rgb))
    rescale_img = (255.0 / my_rgb.max() * (my_rgb - my_rgb.min())).astype(np.uint8)
    im = Image.fromarray(rescale_img)
    im.save(save_path)


dir_list = []
file_list = []
IMG_PATH = ['I:\Sugarcane_Dataset_No_Background\Jun23'] # one or multiple subdataset folders.
# List of subdataset paths, replace it with yours, you can have one or more subdatasets.
# In each subdataset folder, there should have a 'RGB' folder, manually create it.
# In each subdataset folder, there will be multiple subfolders, each sub-folder should contain the
# images of one variety of sugarcane like mentioned in README.md
for index in range(len(IMG_PATH)):
    print(IMG_PATH[index])
    dir_list = []  # store the names of all the folders in the current subdataset.
    file_list = []
    count = 0
    for (root, dirs, files) in os.walk(IMG_PATH[index], topdown=True):
        if len(dirs) != 0:
            dir_list = dirs
        if count > 0:
            li = []
            for i in files:
                if i.endswith('.hdr'):
                    li.append(i)
            file_list.append(li)
        count += 1
    os.chdir(IMG_PATH[index])  # Navigate to current subdataset folder.
    for i in range(len(dir_list)):  # len(dir_list)
        for j in range(len(file_list[i])):  # len(file_list[i])
            img_path = dir_list[i] + "/" + file_list[i][j]
            save_path = "RGB/" + file_list[i][j].split(".")[0] + ".jpeg"
            # An RGB folder should be created in the subdataset folder.
            print(img_path)
            img = envi.open(img_path)
            img = img[:, :, :]
            hsi2rgb_conversion(img, save_path)
