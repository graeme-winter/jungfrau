# /usr/bin/env python3
#
# Pixel Generator
#
# Read Eiger 2XE 9M data set, derive "original" pixels then invert the correction
# process to get a gain estimate and an estimate of the ADC readout. This is
# unlikely to be perfect fidelity as information will be lost

import os
import sys

import hdf5plugin
import h5py
import numpy

import tqdm

# hard coded gain estimates: these are ADU / keV for the three gain modes: the
# wavelength will be used to calculate the "true" gain of ADU / photon
_G0 = 40
_G1 = -1.5
_G2 = -0.1

G0 = 0
G1 = 0
G2 = 0

keV_per_A = 12.398


def get_use_energy(nxs):
    """Get energy from NXS file, use to update gain"""
    with h5py.File(nxs, "r") as f:
        w = f["/entry/instrument/beam/incident_wavelength"][()]
        e = keV_per_A / w
        G0 = _G0 * e
        G1 = _G1 * e
        G2 = _G2 * e


def sum_big_pixels(image):
    """Sum back the values for the big pixels, in place."""

    result = numpy.zeros((256 * 12, 1024 * 3), dtype=numpy.uint16)

    for my in range(6):
        for mx in range(3):
            oy = my * (512 + 38)
            ox = mx * (1028 + 12)

            source = numpy.zeros((516, 1032), dtype=numpy.uint16)
            source[2:-2, 2:-2] = image[oy : oy + 512, ox : ox + 1028]
            module = numpy.zeros((256 * 2, 1024), dtype=numpy.uint16)

            for ny in range(2):
                for nx in range(4):
                    # middle of the ASIC
                    module[
                        ny * 256 + 1 : ny * 256 + 255, nx * 256 + 1 : nx * 256 + 255
                    ] = source[
                        ny * 258 + 2 : ny * 258 + 256,
                        nx * 258 + 2 : ox + nx * 258 + 256,
                    ]
                    # horizontal bar: beware annoying
                    # vertical bars: also annoying


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
