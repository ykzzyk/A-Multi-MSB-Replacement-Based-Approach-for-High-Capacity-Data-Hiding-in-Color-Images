from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
from os import path
import pickle
import sys

sys.path.append('../../')
import util
from operator import xor

original_image = '../../RGB/lena.ppm'


class Owner:
    def __init__(self, image):
        self.image_processing(image)

    def find_optimal_msb(self, px):
        temp = []  # Create list to store tuple (bpp, msb)

        # Iterate MSBs, from MSB == 7 to MSB == 2
        msb = 8
        while msb > 1:
            # Create a 8-bit template of MSB 1s followed by MSB 0s
            template = ((1 << msb) - 1) << (8 - msb)

            # Create location map
            lm = np.zeros(shape=(512, 512), dtype='uint8')
            mm = np.zeros(shape=(512, 512), dtype='uint8')

            # Image processing
            for i in range(512):
                for j in range(512):
                    mm[i, j] = (px[i, j] & 0x80) % 127
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

            # Calculate the data embedding capacity
            dec = (512 * 512 - np.count_nonzero(lm)) * (msb - 1)

            # Get the map sizes
            lm_size = util.map_compression(lm, 'lossless', 'temp', 'location')  # Get the location map size
            mm_size = util.map_compression(mm, 'lossless', 'temp', 'msb')  # Get the msb map size

            if lm_size + mm_size > (512 * 512 - 36 - 4):
                msb -= 1
                continue

            temp.append((dec, msb))  # Append tuple (bpp, msb)

            # Find the most optimal location map
            if dec == max(temp)[0]:
                location_map = lm
                msb_map = mm

            msb -= 1

        # Find the most optimal bpp and MSB
        try:
            dec, msb = max(temp)
        except ValueError:
            dec = 0
            msb = 0
            location_map = np.zeros(shape=(512, 512), dtype='uint8')
            msb_map = np.zeros(shape=(512, 512), dtype='uint8')

        return dec, msb, location_map, msb_map

    def image_processing(self, image):
        # Seperate the original image channels
        r, g, b = util.sepearte_RGB_channels(image)

        try:
            with open('content_owner.pickle', 'rb') as content_owner:
                data = pickle.load(content_owner)
        except FileNotFoundError:
            with open('content_owner.pickle', 'wb') as content_owner:
                pickle.dump('None', content_owner, protocol=pickle.HIGHEST_PROTOCOL)
                data = pickle.load(content_owner)

        if original_image not in data:
            r_dec, r_msb, r_location_map, r_msb_map = self.find_optimal_msb(r)
            g_dec, g_msb, g_location_map, g_msb_map = self.find_optimal_msb(g)
            b_dec, b_msb, b_location_map, b_msb_map = self.find_optimal_msb(b)
            data = {original_image: {
                'r_dec': r_dec,
                'r_msb': r_msb,
                'r_location_map': r_location_map,
                'r_msb_map': r_msb_map,

                'g_dec': g_dec,
                'g_msb': g_msb,
                'g_location_map': g_location_map,
                'g_msb_map': g_msb_map,

                'b_dec': b_dec,
                'b_msb': b_msb,
                'b_location_map': b_location_map,
                'b_msb_map': b_msb_map, }
            }
            with open('content_owner.pickle', 'wb') as content_owner:
                pickle.dump(data, content_owner, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            r_dec = data[original_image]['r_dec']
            r_msb = data[original_image]['r_msb']
            r_location_map = data[original_image]['r_location_map']
            r_msb_map = data[original_image]['r_msb_map']

            g_dec = data[original_image]['g_dec']
            g_msb = data[original_image]['g_msb']
            g_location_map = data[original_image]['g_location_map']
            g_msb_map = data[original_image]['g_msb_map']

            b_dec = data[original_image]['b_dec']
            b_msb = data[original_image]['b_msb']
            b_location_map = data[original_image]['b_location_map']
            b_msb_map = data[original_image]['b_msb_map']

        max_dec = r_dec + g_dec + b_dec
        bpp = max_dec / (512 * 512)
        print(f'The maximum Data Embedding Capacity is {max_dec} bits, and the bpp is {bpp}')

        r_location_map_size = util.map_compression(r_location_map, 'lossless', 'r', 'location')
        g_location_map_size = util.map_compression(g_location_map, 'lossless', 'g', 'location')
        b_location_map_size = util.map_compression(b_location_map, 'lossless', 'b', 'location')

        r_msb_map_size = util.map_compression(r_msb_map, 'lossless', 'r', 'msb')
        g_msb_map_size = util.map_compression(g_msb_map, 'lossless', 'g', 'msb')
        b_msb_map_size = util.map_compression(b_msb_map, 'lossless', 'b', 'msb')

        # Encrypted image
        pixels = np.array(Image.open(image).convert('RGB').getdata())
        util.image_encryption(pixels)
        pixels = pixels.reshape(512, 512, 3)
        img = Image.fromarray(np.uint8(pixels)).convert('RGB')
        img.save('../../Output/LMR/LMR_EI.ppm')

        # Seperate the encrypted image channels
        e_r, e_g, e_b = util.sepearte_RGB_channels('../../Output/LMR/LMR_EI.ppm')

        e_r = e_r.flatten()
        e_g = e_g.flatten()
        e_b = e_b.flatten()

        # Embed the corresponding location map
        util.embed_map('msb_plane', e_r, 'lossless', 'r', 'location')
        util.embed_map('msb_plane', e_g, 'lossless', 'g', 'location')
        util.embed_map('msb_plane', e_b, 'lossless', 'b', 'location')

        # Embed the corresponding MSB map
        util.embed_map('msb_plane', e_r[r_location_map_size:], 'lossless', 'r', 'msb')
        util.embed_map('msb_plane', e_g[g_location_map_size:], 'lossless', 'g', 'msb')
        util.embed_map('msb_plane', e_b[b_location_map_size:], 'lossless', 'b', 'msb')

        # Embed the optimal MSB
        util.embed_optimal_MSB('msb_plane', e_r, r_msb)
        util.embed_optimal_MSB('msb_plane', e_g, g_msb)
        util.embed_optimal_MSB('msb_plane', e_b, b_msb)

        # Hide the size information in the most significant bits (MSBs) of the encrypted image
        util.embed_size_info('msb_plane', e_r[:-4], r_location_map_size)
        util.embed_size_info('msb_plane', e_g[:-4], g_location_map_size)
        util.embed_size_info('msb_plane', e_b[:-4], b_location_map_size)

        util.embed_size_info('msb_plane', e_r[:-22], r_msb_map_size)
        util.embed_size_info('msb_plane', e_g[:-22], g_msb_map_size)
        util.embed_size_info('msb_plane', e_b[:-22], b_msb_map_size)

        # Save the encrypted image
        R = Image.fromarray(e_r.reshape(512, 512))
        G = Image.fromarray(e_g.reshape(512, 512))
        B = Image.fromarray(e_b.reshape(512, 512))

        img = Image.merge('RGB', (R, G, B))
        img.show()
        img.save('../../Output/LMR/LMR_EI.ppm')


if __name__ == '__main__':
    co = Owner(original_image)
