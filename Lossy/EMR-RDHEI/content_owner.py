from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import pickle  # Store the key1

import sys

sys.path.append('../../')
import util


class Content_owner():
    def __init__(self):
        image = '../../RGB/lena.ppm'
        self.image_processing(image)

    def find_optimal_msb(self, px):
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
            lm_size = util.map_compression(lm, 'loss', 'location')
            if lm_size > (512 * 512 - 18 - 3):
                print('File is too big, try next MSB')
                msb -= 1
                continue

            temp.append((dec, msb))  # Append tuple (bpp, msb)

            # Find the most optimal location map
            if dec == max(temp)[0]:
                location_map = lm

            msb -= 1

        # Find the most optimal bpp and MSB
        dec, msb = max(temp)

        print(dec, msb)
        return dec, msb, location_map

    def image_processing(self, image):
        red, green, blue = Image.open(image).convert('RGB').split()
        r = np.array(red)
        g = np.array(green)
        b = np.array(blue)

        r_dec, r_msb, r_location_map = self.find_optimal_msb(r)
        g_dec, g_msb, g_location_map = self.find_optimal_msb(g)
        b_dec, b_msb, b_location_map = self.find_optimal_msb(b)

        max_dec = r_dec + g_dec + b_dec
        bpp = max_dec / (512 * 512 * 3)
        print(f'The maximum Data Embedding Capacity is {max_dec} bits, and the bpp is {bpp}')


co = Content_owner()