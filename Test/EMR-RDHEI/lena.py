from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import pickle
import sys

sys.path.append('../../')
import util
from operator import xor


if __name__ == '__main__':
    # Seperate the original image channels
    r, g, b = util.sepearte_RGB_channels('../../RGB/beeflowr.ppm')
    R = Image.fromarray(r)
    G = Image.fromarray(g)
    B = Image.fromarray(b)
    
    R.save('image_beeflowr_R.png')
    G.save('image_beeflowr_G.png')
    B.save('image_beeflowr_B.png')

    # px = np.array(Image.open('image_beeflowr_B.ppm'))

    # px = px.flatten()

    # for i in range(15):
    #     print(px[i])
