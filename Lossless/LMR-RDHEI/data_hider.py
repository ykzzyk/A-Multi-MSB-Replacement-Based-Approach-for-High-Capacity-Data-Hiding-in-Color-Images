from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import random  # Import random module to generate random numbers
import sys

sys.path.append('../../')
import util


class Hiding_data:
    def __init__(self, image):
        self.extract_info(image)
        self.data_hider()

    def extract_info(self, image):
        # Seperate the original image channels
        self.r, self.g, self.b = util.sepearte_RGB_channels(image)

        self.r_msb = util.extract_optimal_MSB('msb_plane', self.r)
        self.g_msb = util.extract_optimal_MSB('msb_plane', self.g)
        self.b_msb = util.extract_optimal_MSB('msb_plane', self.b)

        self.r_location_map = util.map_extraction('msb_plane', self.r, 'lossless', 'r', 'location')
        self.g_location_map = util.map_extraction('msb_plane', self.g, 'lossless', 'g', 'location')
        self.b_location_map = util.map_extraction('msb_plane', self.b, 'lossless', 'b', 'location')

    def hiding_data(self, px, msb, location_map):
        random.seed(1)
        offset = msb - 1
        template = '1' + '0' * offset + '1' * (7 - offset)
        for i in range(512):
            for j in range(512):
                if location_map[i, j] == 0:
                    # Clear the most siginificant bits, except the first most siginificant bits
                    px[i, j] = px[i, j] & int(template, 2)

                    # Generate information;
                    info = bin(random.randint((1 << offset - 1), (1 << offset) - 1))[2:]

                    # Do a bitwise OR operation to add the info bits
                    px[i, j] = px[i, j] | int('0' + info + '0' * (7 - offset), 2)

        # Store the encrypted image with embeded hiden message
        img = Image.fromarray(px)

        return img

    def data_hider(self):
        R = self.hiding_data(self.r, self.r_msb, self.r_location_map)
        G = self.hiding_data(self.g, self.g_msb, self.g_location_map)
        B = self.hiding_data(self.b, self.b_msb, self.b_location_map)

        img = Image.merge('RGB', (R, G, B))
        img.save('../../Output/LMR/LMR_RDHEI.ppm')


if __name__ == '__main__':
    dh = Hiding_data('../../Output/LMR/LMR_EI.ppm')
