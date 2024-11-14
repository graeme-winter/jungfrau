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

import h5py


def mask_image(image):
    pass


def mask_big_pixels(filename):
    with h5py.File(filename, "r+") as f:
        assert "data" in f
        d = f["data"]
        nz, ny, nx = d.shape
        assert ny == 3262
        assert nx == 3108

        for j in range(nz):
            i = d[j, :, :]
            i = mask_image(i)
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
