from subprocess import call
from PIL import Image  # Import Image from Pillow mudule
import numpy as np  # Import Numpy
import pickle  # Store the key1
import os  # Generate cryptographically secure RNG: os.urandom()
import sys  # Import sys


def user_input():
    key = input('Please type "key1" or "key2" or "key1&key2":\n')

    # If key type is wrong, retype the key
    while key not in ("key1", "key2", "key1&key2"):
        key = input('Please type "key1" or "key2" or "key1&key2" again:\n')

    return key


def load_key1():
    # load key1 from pickle
    with open('key1.pickle', 'rb') as f:
        keystream = pickle.load(f)
    return np.array(keystream).reshape(512, 512)


def image_encryption(pixels):
    """Image Encryption"""
    # Image Encryption
    keystream = []  # Store keys
    for i in range(0, 512):
        for j in range(0, 512):
            key = int.from_bytes(os.urandom(1), byteorder=sys.byteorder)  # Generate cryptographically secure RNG key
            pixels[i, j] ^= key  # Do a bitwise XOR operation to encrypt image
            keystream.append(key)  # Append keys

    # Stroe key1 in pickle
    with open('key1.pickle', 'wb') as f:
        pickle.dump(keystream, f, pickle.HIGHEST_PROTOCOL)


def embed_base_MSB(bit_plane, pixels, msb):
    if bit_plane == 'lsb_plane':
        pixels = pixels.flatten()
        for k, v in enumerate(bin(msb)[2:].zfill(3)):
            if v == '0':
                pixels[-1 - k] &= 0xfe
            else:
                pixels[-1 - k] |= 1

        return pixels.reshape(512, 512)
    else:
        for k, v in enumerate(bin(msb)[2:].zfill(4)):
            if v == '1':
                pixels[-1 - k] |= 128
            else:
                pixels[-1 - k] &= 127


def extract_base_MSB(bit_plane, pixels):
    pixels = pixels.flatten()
    if bit_plane == 'lsb_plane':
        msb = int(''.join([str(pixels[-1 - i] & 1) for i in range(3)]), 2)
    else:
        msb = int(''.join([str((pixels[-1 - i] & 0x80) % 127) for i in range(4)]), 2)

    return msb


def embed_map(bit_plane, pixels, genre, name):
    if bit_plane == 'lsb_plane':
        pixels = pixels.flatten()
        """Embedding map to LSB"""
        to_bytes = open(f'../../Output/TEMP/{genre}_generate_{name}_map.jbg', 'rb').read()
        to_bits = bin(int.from_bytes(to_bytes, byteorder=sys.byteorder))[2:]
        for i in range(len(to_bits)):
            if to_bits[i] == '1':
                pixels[i] |= 1  # hide a 1 bit
            else:
                pixels[i] &= 0xfe  # hide a 0 bit

        return pixels.reshape(512, 512)

    else:
        """Embedding map to MSB"""
        to_bytes = open(f'../../Output/TEMP/{genre}_generate_{name}_map.jbg', 'rb').read()
        to_bits = bin(int.from_bytes(to_bytes, byteorder=sys.byteorder))[2:]
        for i in range(len(to_bits)):
            if to_bits[i] == '1':
                pixels[i] |= 128
            else:
                pixels[i] &= 127


def map_compression(target, genre, name):
    np.set_printoptions(threshold=sys.maxsize)
    target = str(target.flatten()).replace('[', ' ').replace(']', ' ')

    with open(f'../../Output/TEMP/{genre}_write_in_{name}_map.pbm', 'w+') as f:
        f.write(f'P1\n512\n512\n\n{target}')

    call(['../.././pbmtojbg', '-q', f'../../Output/TEMP/{genre}_write_in_{name}_map.pbm',
          f'../../Output/TEMP/{genre}_generate_{name}_map.jbg'])

    # Check the map size
    map_size = os.stat(f'../../Output/TEMP/{genre}_generate_{name}_map.jbg').st_size * 8 - 6

    # Return the size of map size
    return map_size


def embed_size_info(bit_plane, pixels, file_size):
    size = bin(file_size)[2:][::-1]
    if bit_plane == 'lsb_plane':
        pixels = pixels.flatten()
        """Embedding map size info to LSB"""
        for i in range(4, 23):
            pixels[-i] &= 0xfe  # Clear the least most siginificant bit

        for i in range(len(size)):
            pixels[-i - 4] |= int(size[i])
        return pixels.reshape(512, 512)

    else:
        """Embedding map size info to MSB"""
        for i in range(1, 19):
            pixels[-i] &= 127  # Clear the most siginificant bit

        for i in range(len(size)):
            if size[i] == '1':
                pixels[-i - 1] |= 128
            else:
                pixels[-i - 1] &= 127


def map_extraction(bit_plane, pixels, genre, name):
    pixels = pixels.flatten()
    size = ''  # Get size info
    bits = ''  # Get bits info
    if bit_plane == 'lsb_plane':
        """Extract map from the least siginificant bits"""

        # Get all the least siginificant bits and the hidden size information
        for i in range(len(pixels)):
            bits += str(pixels[i] & 1)
            if (len(pixels) - 22 < i) and (len(pixels) - 3 > i):
                size += str(pixels[i] & 1)

        map_size = int(size, 2)  # Get the map size

        # Write into the '*.jbg' file
        byte = int(bits[:map_size], 2).to_bytes((map_size + 7) // 8, byteorder=sys.byteorder)

    else:
        """Extract map from the most siginificant bits"""
        size = "".join([str((pixels[-i] & 0x80) % 127) for i in range(4, 40)])

        # Get the map size
        location_map_size = int(size[:18][::-1], 2)
        msb_map_size = int(size[18:][::-1], 2)

        bits = ''.join([str((pixels[i] & 0x80) % 127) for i in range(len(pixels))])

        if name == 'location':
            byte = int(bits[:location_map_size], 2).to_bytes((location_map_size + 7) // 8, byteorder=sys.byteorder)
        else:
            byte = int(bits[location_map_size:][:msb_map_size], 2).to_bytes((msb_map_size + 7) // 8,
                                                                            byteorder=sys.byteorder)

    # Write the JBG file for decompressing
    with open(f'../../Output/TEMP/{genre}_write_in_{name}_map.jbg', 'wb') as f:
        f.write(byte)

    call(['../.././jbgtopbm', f'../../Output/TEMP/{genre}_write_in_{name}_map.jbg',
          f'../../Output/TEMP/{genre}_generate_{name}_map.pbm'])

    img = Image.open(f'../../Output/TEMP/{genre}_generate_{name}_map.pbm')
    # Decompress the map
    extracted_map = np.invert(np.array(img)).astype('uint8')

    # return the extracted map
    return extracted_map
