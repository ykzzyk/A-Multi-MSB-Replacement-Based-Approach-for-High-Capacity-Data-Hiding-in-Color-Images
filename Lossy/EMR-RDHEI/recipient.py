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
        self.recipient('key1')

    def extract_info(self, image):
        # Seperate the original image channels
        self.r, self.g, self.b = util.sepearte_RGB_channels(image)

        # Extract the optimal MSB
        self.r_msb = util.extract_optimal_MSB('lsb_plane', self.r)
        self.g_msb = util.extract_optimal_MSB('lsb_plane', self.g)
        self.b_msb = util.extract_optimal_MSB('lsb_plane', self.b)

        # Extract the location map
        self.r_location_map = util.map_extraction('lsb_plane', self.r, 'loss', 'r', 'location')
        self.g_location_map = util.map_extraction('lsb_plane', self.g, 'loss', 'g', 'location')
        self.b_location_map = util.map_extraction('lsb_plane', self.b, 'loss', 'b', 'location')

    def extract_message(self, px, msb, location_map):
        random.seed(1)
        template = ((1 << msb) - 1) << (8 - msb)  # Create a 8-bit template of MSB 1s followed by MSB 0s
        for i in range(512):
            for j in range(512):
                if location_map[i, j] == 0:
                    info = (px[i, j] & template) >> (8 - msb)  # Extract the secret message
                    # Compare with the original information
                    if random.randint(0, (1 << msb) - 1) != info:
                        print("Message extracted is NOT the same as that added")
                        sys.exit(1)  # If message not equal, exit the system

        # Extract message with no errors
        print('Message extract successfully!')

    def channel_reconstruction(self, px, msb, location_map):
        template = ((1 << msb) - 1) << (8 - msb)
        for i in range(512):
            for j in range(512):
                if location_map[i, j] == 1:
                    mark = px[i, j] & template  # Create marks to store the MSB infomation
                else:
                    px[i, j] &= ((1 << (8 - msb)) - 1)  # Clear the most siginificant bits
                    px[i, j] |= mark  # Reconstruct the pixels

                # Store the image
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
        img.save('../../Output/EMR/Decrypted_EMR_RDHEI.ppm')

        # Seperate the three channels
        r, g, b = util.sepearte_RGB_channels('../../Output/EMR/Decrypted_EMR_RDHEI.ppm')

        R = self.channel_reconstruction(r, self.r_msb, self.r_location_map)
        G = self.channel_reconstruction(g, self.g_msb, self.g_location_map)
        B = self.channel_reconstruction(b, self.b_msb, self.b_location_map)

        image = Image.merge('RGB', (R, G, B))
        image.save('EMR_R.ppm')

    def recipient(self, key):

        if key == 'key1':
            self.image_reconstruction('../../Output/EMR/EMR_RDHEI.ppm')
            eval.skimage_psnr(self.original_image, 'EMR_R.ppm')

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
            self.image_reconstruction('../../Output/EMR/EMR_RDHEI.ppm')
            eval.skimage_psnr(self.original_image, 'EMR_R.ppm')


if __name__ == '__main__':
    rc = Receiver('../../Output/EMR/EMR_RDHEI.ppm', content_owner.original_image)
