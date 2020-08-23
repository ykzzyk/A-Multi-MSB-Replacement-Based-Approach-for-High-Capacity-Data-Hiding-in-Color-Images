from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import random  # Import random module to generate random numbers
import sys

sys.path.append('../../')
import util


class hiding_data:
    def __init__(self, image):
        self.extract_info(image)
        self.data_hider()

    def extract_info(self, image):
        # Seperate the original image channels
        self.r, self.g, self.b = util.sepearte_RGB_channels(image)

        self.r_msb = util.extract_optimal_MSB('lsb_plane', self.r)
        self.g_msb = util.extract_optimal_MSB('lsb_plane', self.g)
        self.b_msb = util.extract_optimal_MSB('lsb_plane', self.b)

        self.r_location_map = util.map_extraction('lsb_plane', self.r, 'loss', 'r', 'location')
        self.g_location_map = util.map_extraction('lsb_plane', self.g, 'loss', 'g', 'location')
        self.b_location_map = util.map_extraction('lsb_plane', self.b, 'loss', 'b', 'location')

    def hiding_data(self, px, msb, location_map):
        random.seed(1)
        for i in range(512):
            for j in range(512):
                # If location map[i] == 0, we can embed the secret message into the MSBs
                if location_map[i, j] == 0:
                    px[i, j] &= ((1 << (8 - msb)) - 1)  # Clear the most siginificant bits

                    info = random.randint(0, (1 << msb) - 1) << (8 - msb)  # Generate the secret message

                    px[i, j] |= info  # Do a bitwise OR operation to add the info bits

        # Store the encrypted image with embeded hiden message
        img = Image.fromarray(px)

        return img

    def data_hider(self):
        R = self.hiding_data(self.r, self.r_msb, self.r_location_map)
        G = self.hiding_data(self.g, self.g_msb, self.g_location_map)
        B = self.hiding_data(self.b, self.b_msb, self.b_location_map)

        img = Image.merge('RGB', (R, G, B))
        img.save('../../Output/EMR/EMR_RDHEI.ppm')


dh = hiding_data('../../Output/EMR/EMR_EI.ppm')
