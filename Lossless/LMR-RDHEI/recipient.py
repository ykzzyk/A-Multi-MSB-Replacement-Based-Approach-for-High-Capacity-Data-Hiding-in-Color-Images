from PIL import Image  # Import Image from Pillow mudule
from operator import xor
import content_owner
import numpy as np  # Import Numpy
import random  # Import random module to generate random numbers
import sys

sys.path.append('../../')
import util
import eval


class Receiver:
    def __init__(self, image, original_image):
        self.original_image = original_image
        self.extract_info(image)
        self.recipient('key1&key2')

    def extract_info(self, image):
        # Seperate the original image channels
        self.r, self.g, self.b = util.sepearte_RGB_channels(image)

        # Extract the optimal MSB
        self.r_msb = util.extract_optimal_MSB('msb_plane', self.r)
        self.g_msb = util.extract_optimal_MSB('msb_plane', self.g)
        self.b_msb = util.extract_optimal_MSB('msb_plane', self.b)

        # Extract the location map
        self.r_location_map = util.map_extraction('msb_plane', self.r, 'lossless', 'r', 'location')
        self.g_location_map = util.map_extraction('msb_plane', self.g, 'lossless', 'g', 'location')
        self.b_location_map = util.map_extraction('msb_plane', self.b, 'lossless', 'b', 'location')

        # Extract the MSB map
        self.r_msb_map = util.map_extraction('msb_plane', self.r, 'lossless', 'r', 'msb')
        self.g_msb_map = util.map_extraction('msb_plane', self.g, 'lossless', 'g', 'msb')
        self.b_msb_map = util.map_extraction('msb_plane', self.b, 'lossless', 'b', 'msb')

    def extract_message(self, px, msb, location_map):
        random.seed(1)

        offset = msb - 1

        info_temp = int('1' + '0' * offset + '1' * (7 - offset), 2)

        for i in range(512):
            for j in range(512):
                if location_map[i, j] == 0:
                    info = int(bin(px[i, j] | info_temp)[2:][1:msb], 2)  # Extract the secret message
                    # Compare with the original information
                    if random.randint((1 << offset - 1), (1 << offset) - 1) != info:
                        print("Message extracted is NOT the same as that added")
                        sys.exit(1)  # If message not equal, exit the system

        # Extract message with no errors
        print('Message extract successfully!')

    def channel_reconstruction(self, px, msb, location_map, msb_map):
        # Create a 8-bit template of MSB 1s followed by MSB 0s
        template = ((1 << msb) - 1) << (8 - msb)
        for i in range(512):
            for j in range(512):
                # Substitude the MSB
                if msb_map[i, j] == 1:
                    px[i, j] |= 128
                else:
                    px[i, j] &= 127

                if location_map[i, j] == 1:
                    mark = px[i, j] & template  # Create marks to store the MSB infomation
                else:
                    px[i, j] &= ((1 << (8 - msb)) - 1)  # Clear the most siginificant bits
                    px[i, j] |= mark  # Reconstruct the pixels

        channel = Image.fromarray(px)

        return channel

    def image_reconstruction(self, image):
        # Image Decryption
        pixels = np.array(Image.open(image).convert('RGB').getdata())
        keystream = util.load_key1()
        for idx in range(0, 512 * 512):
            pixels[idx] = list(map(xor, pixels[idx], keystream[idx]))

        pixels = pixels.reshape(512, 512, 3)

        img = Image.fromarray(np.uint8(pixels)).convert('RGB')
        img.save('../../Output/LMR/Decrypted_LMR_RDHEI.ppm')

        # Seperate the three channels
        r, g, b = util.sepearte_RGB_channels('../../Output/LMR/Decrypted_LMR_RDHEI.ppm')

        R = self.channel_reconstruction(r, self.r_msb, self.r_location_map, self.r_msb_map)
        G = self.channel_reconstruction(g, self.g_msb, self.g_location_map, self.g_msb_map)
        B = self.channel_reconstruction(b, self.b_msb, self.b_location_map, self.b_msb_map)

        image = Image.merge('RGB', (R, G, B))
        image.save('../../Output/LMR/LMR_R.ppm')

    def recipient(self, key):

        if key == 'key1':
            self.image_reconstruction('../../Output/LMR/LMR_RDHEI.ppm')
            eval.skimage_psnr(self.original_image, '../../Output/LMR/LMR_R.ppm')

        elif key == 'key2':
            self.extract_message(self.r, self.r_msb, self.r_location_map)
            self.extract_message(self.g, self.g_msb, self.g_location_map)
            self.extract_message(self.b, self.b_msb, self.b_location_map)

        elif key == 'key1&key2':
            # Extract Message
            self.extract_message(self.r, self.r_msb, self.r_location_map)
            self.extract_message(self.g, self.g_msb, self.g_location_map)
            self.extract_message(self.b, self.b_msb, self.b_location_map)

            # Reconstruct image
            self.image_reconstruction('../../Output/LMR/LMR_RDHEI.ppm')
            eval.skimage_psnr(self.original_image, '../../Output/LMR/LMR_R.ppm')


rc = Receiver('../../Output/LMR/LMR_RDHEI.ppm', content_owner.original_image)
