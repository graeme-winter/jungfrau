# /usr/bin/env python3
#
# Big Pixel Masker
#
# Mask the "big" pixels in an Eiger 9M data set to recreate the effect of
# not considering the big pixels for Jungfrau 9M: can be applied to rotation
# data from a Si or CdTe Eiger, or SSX data.
#
# Usage:
#
# python3 big_pixel_masker.py foo_00001.h5
#
# Will make a backup of the file then rewrite the data set with the big
# pixels set to -1

import os
import shutil
import sys

import hdf5plugin
import h5py

import tqdm


def mask_image(image):
    """In place over-write unpacked big pixels with values of -1"""

    for my in range(6):
        for mx in range(3):
            oy = my * (512 + 38)
            ox = mx * (1028 + 12)

            # horizontal bar
            image[oy + 254 : oy + 258, ox : ox + 1028] = 0xFFFF

            # 3 x vertical bars
            image[oy : oy + 512, ox + 254 : ox + 258] = 0xFFFF
            image[oy : oy + 512, ox + 512 : ox + 516] = 0xFFFF
            image[oy : oy + 512, ox + 770 : ox + 774] = 0xFFFF


def mask_big_pixels(filename):
    """Mask the unpacked big pixels on every frame of an Eiger 9M data set"""

    with h5py.File(filename, "r+") as f:
        assert "data" in f
        d = f["data"]
        nz, ny, nx = d.shape
        assert ny == 3262
        assert nx == 3108

        for j in tqdm.tqdm(range(nz)):
            i = d[j, :, :]
            mask_image(i)
            d[j, :, :] = i


def main(filename):

    assert filename.endswith(".h5")
    copy = f"{filename[:-3]}.bck"

    assert os.path.exists(filename)
    assert not os.path.exists(copy)

    shutil.copyfile(filename, copy)

    mask_big_pixels(filename)


if __name__ == "__main__":
    main(sys.argv[1])
