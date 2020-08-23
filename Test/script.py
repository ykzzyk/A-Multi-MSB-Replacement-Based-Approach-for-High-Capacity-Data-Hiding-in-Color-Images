from PIL import Image
import numpy as np
import sys

sys.path.append('../')
import eval


# pixel = Image.open('SanFrancisco.tiff').convert('RGB').getpixel((0, 0))
# print(pixel)

pixels = np.array(Image.open('SanFrancisco.tiff').convert('RGB').getdata())
print(pixels)


R, G, B = Image.open('SanFrancisco.tiff').convert('RGB').split()
r = np.array(R)
g = np.array(G)
b = np.array(B)

R = Image.fromarray(r)
G = Image.fromarray(g)
B = Image.fromarray(b)

# merge funstion used
im1 = Image.merge('RGB', (R, G, B))
im1.show()
im1.save('im1.tiff')

# Calculate PSNR
eval.skimage_psnr('SanFrancisco.tiff', 'im1.tiff')