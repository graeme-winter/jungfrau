import sys

import h5py
import hdf5plugin
import numpy
import tqdm

ny, nx = 512, 1028
gy, gx = 38, 12

mx = 0
my = 0


def uncorrect_module(module):
    assert module.shape == (512, 1028), module.shape
    result = numpy.zeros((512, 1024), dtype=numpy.uint16)

    for ny in range(2):
        for nx in range(4):
            # middle of the ASIC
            result[
                ny * 256 + 1 : ny * 256 + 255, nx * 256 + 1 : nx * 256 + 255
            ] = module[
                ny * 258 : ny * 258 + 254,
                nx * 258 : nx * 258 + 254,
            ]

    return result


with h5py.File(sys.argv[1], "r") as f:
    total = None

    data = f["/entry/data/data"]

    for j in 2, 3, 4:
        mx, my = j, 2 * j
        if (data.shape[1] == my * ny + (my - 1) * gy) and (
            data.shape[2] == mx * nx + (mx - 1) * gx
        ):
            break
    assert mx != 0 and my != 0, (mx, my)

    for i in tqdm.tqdm(range(data.shape[0])):
        stack = numpy.zeros(dtype=numpy.uint16, shape=(my * mx, 512, 1024))
        frame = data[i][()]
        for j in range(my * mx):
            x = j // my
            y = j % my

            module = frame[
                y * (ny + gy) : y * (ny + gy) + ny, x * (nx + gx) : x * (nx + gx) + nx
            ]
            module = uncorrect_module(module)
            stack[j] = module

        stack = stack.reshape((my * mx * 512 * 1024,))
