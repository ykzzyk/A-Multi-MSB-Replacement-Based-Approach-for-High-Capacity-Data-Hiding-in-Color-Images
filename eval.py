from PIL import Image
from skimage import metrics
from matplotlib import pyplot as plt
from scipy import stats
import xlsxwriter
import pandas as pd
import numpy as np
import math


#--------------------------Excel
# Create different worksheet
def excelsheet(arr, filename):
    df = pd.DataFrame(arr)
    df.to_excel(excel_writer=f"{filename}.xlsx")


#--------------------------Calculates
# Calculate the MSE
def skimage_mse(sample, contrast):
    sample_data = Image.open(sample)
    sample_arr = np.array(sample_data)

    contrast_data = Image.open(contrast)
    contrast_arr = np.array(contrast_data)

    mse = metrics.mean_squared_error(sample_arr, contrast_arr)
    print(f"The Mean Squared Error is: {mse}")
    return mse


# Calculate the PSNR
def skimage_psnr(sample, contrast):
    sample_data = Image.open(sample)
    sample_arr = np.array(sample_data)

    contrast_data = Image.open(contrast)
    contrast_arr = np.array(contrast_data)

    psnr = metrics.peak_signal_noise_ratio(sample_arr, contrast_arr, data_range=None)
    print(f"The Peak Signal-to-Noise Ratio is: {psnr}")
    return psnr


def calculate_psnr(mse):
    res = 10 * math.log(255 ** 2/mse, 10)
    print(f"The Peak Signal-to-Noise Ratio is: {res}")


# Calculate the SSIM
def skimage_ssim(sample, contrast):
    sample_data = Image.open(sample)
    sample_arr = np.array(sample_data)

    contrast_data = Image.open(contrast)
    contrast_arr = np.array(contrast_data)

    ssim = metrics.structural_similarity(sample_arr, contrast_arr, data_range=1, multichannel=True, win_size=3)
    print(f"The Structural SIMilarity is: {ssim}")
    return ssim


def shannon_entropy(arr):
    res = 0
    for i in range(256):
        if i in arr:
            p = (arr.count(i))/(512 * 512)
            res += p * math.log(p, 2)

    print(f"The Shannon Entropy is: {-res}")


def chisquare(arr):
    total = 0
    for i in range(256):
        if i in arr:
            p = (arr.count(i)) / (512 * 512)
            total += (p - 1/256) ** 2

    res = 256 * 512 * 512 * total
    print(f"The chisquare is: {res}")


def NPCR(sample, contrast):
    total = 0
    for i in range(len(sample)):
        if sample[i] != contrast[i]:
            total += 1

    res = total / (512 * 512)
    print(f'The NPCR is: {res}')


def UACI(sample, contrast):
    total = 0
    for i in range(len(sample)):
        total += abs(int(sample[i]) - int(contrast[i])) / 255

    res = total / (512 * 512)
    print(f'The UACI is: {res}')


#--------------------------Plots
def plot_bpp(x_axis, y_axis, x_label, y_label, x_length, y_length, filepath):
    my_figure = plt.figure(figsize=[30, 10])

    ax = my_figure.add_subplot(1, 1, 1)

    # Removing top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Re-directioning ticks inward
    ax.tick_params(direction="in")

    plt.plot(x_axis, y_axis, color="blue")
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.xlim(0, x_length)
    plt.ylim(0, y_length)

    plt.savefig(filepath, dpi=200)


def plot_psnr(x_axis, y_axis, x_label, y_label, x_length, filepath):
    plt.plot(x_axis, y_axis)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.xlim(0, x_length)
    plt.ylim(40, 90)

    plt.savefig(filepath)

