from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import sys

sys.path.append('../../')
import util
from operator import xor

original_image = '../../RGB/lena.ppm'


class Owner:
    def __init__(self, image):
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
            lm_size = util.map_compression(lm, 'loss', 'temp', 'location')
            if lm_size > (512 * 512 - 18 - 3):
                print(f'current MSB is {msb}, file is too big, try next MSB')
                msb -= 1
                continue

            temp.append((dec, msb))  # Append tuple (bpp, msb)

            # Find the most optimal location map
            if dec == max(temp)[0]:
                location_map = lm

            msb -= 1

        # Find the most optimal MSB and the maximum DEC
        dec, msb = max(temp)

        return dec, msb, location_map

    def image_processing(self, image):
        # Seperate the original image channels
        r, g, b = util.sepearte_RGB_channels(image)

        r_dec, r_msb, r_location_map = self.find_optimal_msb(r)
        g_dec, g_msb, g_location_map = self.find_optimal_msb(g)
        b_dec, b_msb, b_location_map = self.find_optimal_msb(b)

        max_dec = r_dec + g_dec + b_dec
        bpp = max_dec / (512 * 512)
        print(f'The maximum Data Embedding Capacity is {max_dec} bits, and the bpp is {bpp}')

        # Encrypted image
        pixels = np.array(Image.open(image).convert('RGB').getdata())
        util.image_encryption(pixels)
        pixels = pixels.reshape(512, 512, 3)
        img = Image.fromarray(np.uint8(pixels)).convert('RGB')
        img.save('../../Output/EMR/EMR_EI.ppm')

        '''
        # Decryption
        pxs = np.array(Image.open('EMR_EI.ppm').convert('RGB').getdata())
        keystream = util.load_key1()
        for idx in range(0, 512 * 512):
            pxs[idx] = list(map(xor, pxs[idx], keystream[idx]))

        pxs = pxs.reshape(512, 512, 3)
        img = Image.fromarray(np.uint8(pxs)).convert('RGB')
        img.show()
        img.save('Decrypted_EMR_EI.ppm')
        '''

        # Seperate the encrypted image channels
        e_r, e_g, e_b = util.sepearte_RGB_channels('../../Output/EMR/EMR_EI.ppm')

        r_location_map_size = util.map_compression(r_location_map, 'loss', 'r', 'location')
        g_location_map_size = util.map_compression(g_location_map, 'loss', 'g', 'location')
        b_location_map_size = util.map_compression(b_location_map, 'loss', 'b', 'location')

        # Embed the corresponding location map
        e_r = util.embed_map('lsb_plane', e_r, 'loss', 'r', 'location')
        e_g = util.embed_map('lsb_plane', e_g, 'loss', 'g', 'location')
        e_b = util.embed_map('lsb_plane', e_b, 'loss', 'b', 'location')

        # Embed size of the location map into the last 18 least siginificant bits
        e_r = util.embed_size_info('lsb_plane', e_r, r_location_map_size)
        e_g = util.embed_size_info('lsb_plane', e_g, g_location_map_size)
        e_b = util.embed_size_info('lsb_plane', e_b, b_location_map_size)

        # Embed the optimal MSB
        e_r = util.embed_optimal_MSB('lsb_plane', e_r, r_msb)
        e_g = util.embed_optimal_MSB('lsb_plane', e_g, g_msb)
        e_b = util.embed_optimal_MSB('lsb_plane', e_b, b_msb)

        # Save the encrypted image
        R = Image.fromarray(e_r)
        G = Image.fromarray(e_g)
        B = Image.fromarray(e_b)

        img = Image.merge('RGB', (R, G, B))
        img.save('../../Output/EMR/EMR_EI.ppm')


if __name__ == '__main__':
    co = Owner(original_image)
