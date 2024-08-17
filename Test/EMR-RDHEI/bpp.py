from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import pickle
import tqdm
import sys
import os

sys.path.append('../../')
import util
from operator import xor

DATA = {'file_path': [], 'msb': [], 'bpp': []}


def find_optimal_msb(px):
    temp = []
    # Iterate MSBs, from MSB == 7 to MSB == 2
    msb = 7
    while msb > 1:
        # Create a 8-bit template of MSB 1s followed by MSB 0s
        template = ((1 << msb) - 1) << (8 - msb)

        # Create location map
        lm = np.zeros(shape=(512, 512), dtype='uint8')

        # Image processing
        for i in range(512):
            for j in range(512):
                if i == 0 and j == 0:
                    # Mark the first pixel in the location map: "1"
                    lm[i, j] = 1
                    mark = px[i, j]
                    continue
                # MSB doesn't match
                if px[i, j] & template != mark & template:
                    # Mark the pixels in the location map: "1"
                    lm[i, j] = 1
                    mark = px[i, j]

        dec = (512 * 512 - np.count_nonzero(lm)) * msb  # Data Embedding Capacity
        lm_size = util.map_compression(lm, 'loss', 'temp', 'location')
        if lm_size > (512 * 512 - 18 - 3):
            print(f'current MSB is {msb}, file is too big, try next MSB')
            msb -= 1
            continue

        temp.append((dec, msb))  # Append tuple (bpp, msb)

        msb -= 1

    # Find the most optimal MSB and the maximum DEC
    dec, msb = max(temp)

    return dec, msb


def test_bpp(image):
    DATA['file_path'].append(image)
    # Seperate the original image channels
    r, g, b = util.sepearte_RGB_channels(image)

    r_dec, r_msb = find_optimal_msb(r)
    g_dec, g_msb = find_optimal_msb(g)
    b_dec, b_msb = find_optimal_msb(b)

    max_dec = r_dec + g_dec + b_dec
    bpp = max_dec / (512 * 512)

    DATA['msb'].append((r_msb, g_msb, b_msb))
    DATA['bpp'].append(bpp)


if __name__ == '__main__':

    try:
        with open('test_emr_bpp.pickle', 'rb') as handle:
            data = pickle.load(handle)
            maximum_bpp = max(data['bpp'])
            minimum_bpp = min(data['bpp'])
            average_bpp = sum(data['bpp']) / len(data['bpp'])
    except FileNotFoundError:
        for image in tqdm.tqdm(os.listdir('../../RGB/')):

            if 'ppm' not in image:
                continue

            try:
                test_bpp('../../RGB/' + image)
            except:
                continue

        with open('test_emr_bpp.pickle', 'wb') as handle:
            pickle.dump(DATA, handle, protocol=pickle.HIGHEST_PROTOCOL)

        maximum_bpp = max(DATA['bpp'])
        minimum_bpp = min(DATA['bpp'])
        average_bpp = sum(DATA['bpp']) / len(DATA['bpp'])

    print(f'the maximum bpp is {maximum_bpp}\nthe average bpp is {average_bpp}\nthe minimum bpp is {minimum_bpp}')
