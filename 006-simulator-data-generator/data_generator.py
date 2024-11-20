#!/usr/bin/env python3
#
# Data Generator: convert an EIGER data set (ideally from a 9M Eiger 2) into
# a format consistent with the "raw" format from the SLS frame receiver i.e.
# 112 byte header (where we only fill in the first 8 bytes with the frame
# number) and the binary data for a half-module reverse-corrected to approximate
# ADC readout values.

import sys

import h5py
import hdf5plugin
import numpy
import tqdm

# constants 1: EIGER 2X module parameters, gaps - numbers of modules will be
# determined from the array size from the input HDF5 file
ny, nx = 512, 1028
gy, gx = 38, 12

mx = 0
my = 0

# reasonable values for the three gains in ADU / keV, hard coded for the
# photon energy on i04-1
G0E = 40 * 13.504
G1E = -1.5 * 13.504
G2E = -0.1 * 13.504

# reasonable values for the pedestal at the three gain modes: here these will
# be considered as constants but in real life they vary from pixel to pixel
P0 = 3000
P1 = 15000
P2 = 15000


def count_to_adc(stack):
    """Convert counts back to ADC readouts and gain mode"""
    mask = stack < 0xFFFE
    stack *= mask

    # which gain modes would be appropriate for each pixel (approximate)
    g0 = (stack >= 0) & (stack < 25)
    g1 = (stack >= 25) & (stack < 700)
    g2 = stack >= 700

    result = (
        (stack * g0 * G0E + g0 * P0)
        + (stack * g1 * G1E + g1 * P1)
        + (stack * g2 * G2E + g2 * P2)
    ).astype(numpy.uint16)

    # add the gain bits and re-mask the result (assume readout of exactly zero
    # is masked value)
    result += (g1 * (1 << 14) + g2 * (3 << 14)).astype(numpy.uint16)
    result *= mask

    return result


def uncorrect_module(module):
    """Re-shape pixels from a module back to something similar to the readout"""

    assert module.shape == (512, 1028), module.shape
    result = numpy.zeros((512, 1024), dtype=numpy.uint16)

    for ny in range(2):
        for nx in range(4):
            # middle of the ASIC
            result[ny * 256 + 1 : ny * 256 + 255, nx * 256 + 1 : nx * 256 + 255] = (
                module[
                    ny * 258 : ny * 258 + 254,
                    nx * 258 : nx * 258 + 254,
                ]
            )
            # FIXME address the horizontal and three vertical bars of big pixels
            # which need to be summed across either 2x1, 1x2 or 2x2 virtual pixels

    return result


def main(filename, output_template):

    with h5py.File(filename, "r") as f:
        data = f["/entry/data/data"]

        # guess the number of modules, though in ths case we are only really
        # interested in 9M detector, so 6 x 3 modules
        for j in 2, 3, 4:
            mx, my = j, 2 * j
            if (data.shape[1] == my * ny + (my - 1) * gy) and (
                data.shape[2] == mx * nx + (mx - 1) * gx
            ):
                break
        assert mx != 0 and my != 0, (mx, my)

        # open one file for every half module
        fouts = [open(output_template % j, "wb") for j in range(my * mx * 2)]

        # convert the data to raw files
        for i in tqdm.tqdm(range(data.shape[0])):
            header = numpy.zeros((14,), dtype=numpy.uint64)
            header[0] = i
            stack = numpy.zeros(dtype=numpy.uint16, shape=(my * mx, 512, 1024))
            frame = data[i][()]

            # reshape the data into a stack: extract pixels and stack up
            for j in range(my * mx):
                x = j // my
                y = j % my

                module = frame[
                    y * (ny + gy) : y * (ny + gy) + ny,
                    x * (nx + gx) : x * (nx + gx) + nx,
                ]
                module = uncorrect_module(module)
                stack[j] = module

            # reshape into half-modules, correct and write to the binary output files
            stack = stack.reshape(
                (
                    my * mx * 2,
                    256 * 1024,
                )
            )
            stack = count_to_adc(stack)
            for j in range(my * mx * 2):
                fouts[j].write(header.tobytes())
                fouts[j].write(stack[j].tobytes())

        # clean up
        for fout in fouts:
            fout.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
