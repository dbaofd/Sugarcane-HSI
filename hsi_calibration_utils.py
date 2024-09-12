from spectral import *
import matplotlib.pyplot as plt
import math
import numpy as np
from skimage import morphology


class WhiteBoardPixel:
    """
    For white calibration we need to find 1000 brightest pixel,
    this class defines the object for a white board pixel.
    """

    def __init__(self, l2norm, row, column):
        """
        :param l2norm: l2norm value of a pixel vector.
        :param row: y axis value, coordinate of the pixel
        :param column: x axis value, coordinate of the pixel
        """
        self.l2norm = l2norm
        self.row = row
        self.column = column


def dark_calibration(img_path, dark_ref_path):
    """
    Perform dark calibration. Subtract dark reference is the first
    step as it removes the camera noise from the image.
    :param img_path: hsi image path
    :param dark_ref_path: dark reference path
    :return: dark-calibrated image as numpy array, image metadata
    """
    print("Begin dark calibration")
    dark_reference = envi.open(dark_ref_path)  # envi is used to load hsi image in python.
    img = envi.open(img_path)
    img_as_np = img[:, :, :]
    dark_reference_as_np = dark_reference[:, :, :]
    print("Finish dark calibration")
    return img_as_np - dark_reference_as_np, img.metadata


def display_label(m, title):
    """
    Display identified white board in the hsi image.
    :param m: binary label of a hsi image, foreground pixels belong to the while board.
    :param title: title of the plot.
    """
    label = np.zeros((len(m), len(m[0]), 3))
    for index_i, item_i in enumerate(m):
        for index_j, item_j in enumerate(item_i):
            if item_j == 1:
                label[index_i][index_j][0] = 255
                label[index_i][index_j][1] = 0
                label[index_i][index_j][2] = 255
    label = np.asarray(label, np.intc)
    plt.figure(figsize=(6.5, 6.5))
    plt.title(title)
    plt.imshow(label)


def morphology_operation(m):
    """
    Remove white board pixels at the edge of white board, these white board
    pixels are usually not with good quality.
    :param m: binary label, same spatial dimension as the hsi image,
    foreground is 1 represent while board, background is 0.
    :return: new binary label.
    """
    # display_label(m, "Before")
    processed = morphology.remove_small_objects(m.astype(bool), min_size=5000, connectivity=1).astype(int)
    # black out pixels
    mask_x, mask_y = np.where(processed == 0)
    m[mask_x, mask_y] = 0
    # display_label(m, "After removing small objects")
    kernel = morphology.disk(9)
    for i in range(5):
        m = morphology.erosion(m, kernel)
    display_label(m, "After doing erosion")
    return m


#
def find_brightest_pixel(img_as_np):
    """
    Perform the k-means clustering to find the white board in a hsi image,
    and find the brightest pixels.
    :param img_as_np: hsi image array
    :return: pixel_list: list of white board pixels which are stored in descending order.
    """
    itertion_time = 4
    (m, c) = kmeans(img_as_np, 2, itertion_time, distance='L2')  # k is set to 2, 4 iterations.
    # display_label(m, "Kmeans result")\
    white_board_label = 1
    if np.sum(c[0]) > np.sum(c[1]):
        # Find which one is the white board centroid
        # in this case c[0] is the white board centroid because white board pixels
        # have the highest power intensity in a hsi image.
        # The following for loop make sure white board label to be one.
        # In the following steps, we will use morphology operation, 0 will be treated
        # as background, while 1 will be treated as object.
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                if m[i][j] == 0:  # since c[0] is the white board centroid, we reset white board pixel label to 1.
                    m[i][j] = 1
                elif m[i][j] == 1:
                    m[i][j] = 0
    # else if c[1] is the white board centroid, then do nothing, white board pixel label is already 1.
    m = morphology_operation(m)
    # plot initial mean curve of white board pixels.
    plt.figure()
    plt.plot(c[1])
    plt.title("White board cluster centroid curve")
    plt.grid()
    pixel_list = []  # A list for all the white board pixels
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if m[i][j] == white_board_label:
                p = WhiteBoardPixel(np.linalg.norm(img_as_np[i][j]), i, j)
                pixel_list.append(p)
    pixel_list.sort(key=lambda x: x.l2norm, reverse=True)  # Sort list by using l2norm as key in descending order
    return pixel_list


def get_mean_curve_of_white_board(img_as_np):
    """
    Calculate the mean curve of the white board.
    :param img_as_np: a dark-calibrated hsi image as in numpy array.
    :return: the mean curve of the white board in a hsi image.
    """
    pixel_list = find_brightest_pixel(img_as_np)  # Descending order
    mean_curve = np.zeros((1, 1, 161))
    size_of_list = len(pixel_list)
    top_1_percent = math.ceil(size_of_list * 0.01)  # Remove top 1% brightest pixels
    number_of_brightest_pixels = 1000
    for i in range(top_1_percent, top_1_percent + number_of_brightest_pixels, 1):
        mean_curve += img_as_np[pixel_list[i].row][pixel_list[i].column]
    mean_curve /= number_of_brightest_pixels
    return mean_curve


def white_calibration(normalized_img, metadata, save_path):
    """
    Perform white calibration, new "hdr", "raw" files will be saved.
    :param normalized_img: dark-calibrated hsi image as in numpy array.
    :param metadata: meta data of the original hsi image.
    :param save_path: path to save the white calibrated hsi image.
    """
    print("Begin white calibration")
    mean_vector = get_mean_curve_of_white_board(normalized_img)
    # plot the final mean curve.
    plt.figure()
    plt.plot(mean_vector[0][0])
    plt.title("Final mean curve of " + save_path)
    plt.grid()
    for i in range(normalized_img.shape[0]):
        for j in range(normalized_img.shape[1]):
            normalized_img[i, j, :] = normalized_img[i, j, :] / mean_vector
    envi.save_image(save_path, normalized_img, dtype=np.float32, metadata=metadata, force=True, ext='.raw',
                    interleave='BSQ')
    print("Finish white calibration")


def modify_hdr(save_path):
    """
    hdr file saved via envi has a minor issue which causes the
    wavelength info cannot be loaded in the Scyven software.
    This function fixed the issue in hdr file.
    :param save_path: path for the hdr file.
    """
    file = open(save_path, "r")
    contents = file.read()
    strs = contents.split("\n")
    wave_length = strs[13]
    wave_length = wave_length.split("{")
    wave_length = wave_length[0] + "{\n" + wave_length[1]
    strs[13] = wave_length
    new_contents = ""
    for i in range(len(strs)):
        new_contents = new_contents + strs[i] + "\n"
    file.close()
    file = open(save_path, "w")
    file.write(new_contents)
    file.close()
