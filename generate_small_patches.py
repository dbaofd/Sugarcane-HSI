"""
This script is used to generate small hsi patches.
Given a subdataset with all the image being preprocessed.
Manually create new subdataset folder (including the folders inside) for storing image patches.
This script can load a txt file which contains coordinates of every qualified image patch, then
based on these coordinate, image patches can be extracted from original hsi images, and then saved.
"""
from spectral import *
import numpy as np
from hsi_calibration_utils import modify_hdr

IMG_PATH="D:\Sugarcane_Dataset\Apr22/"
SAVING_PATH="F:\Sugarcane_Image_Patch\Apr22_patches/"
WINDOWS_SIZE=32# size of image patch
f=open("F:\mosaic_coordinates/Apr22_small_mosaic.txt") # load the generated coordinates, it follows a format defined by the coordinate generation file.
f_list=[]
for line in f:# load all the coordinate into the list.
    f_list.append((line.split('+')[0],line.split('+')[1]))
f.close()

def save_patches(path, coordinates):
    """
    @param path: original file path
    @param coordinates: list of coordinates of all the image patches in the subdataset.
    """
    img = envi.open(IMG_PATH+path)
    meta_data=img.metadata
    meta_data['samples']=str(WINDOWS_SIZE)
    meta_data['lines']=str(WINDOWS_SIZE)
    coordinates_str_arr=coordinates.split("*")
    print(path)
    for index, item in enumerate(coordinates_str_arr):
        xy=item.split(" ")
        x=int(xy[0])
        y=int(xy[1])
        new_img = img[x:x+WINDOWS_SIZE, y:y+WINDOWS_SIZE]
        save_path=SAVING_PATH+path.split(".")[0]+"_"+str(index)+".hdr"
        envi.save_image(save_path, new_img, dtype=np.float32, metadata=meta_data,force=True, ext='.raw',interleave='BSQ')
        modify_hdr(save_path)
    print("Finish window-sliding")

for li in f_list:
    save_patches(li[0], li[1])


