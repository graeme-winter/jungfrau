import sys

import h5py
import hdf5plugin
import numpy
import tqdm

ny, nx = 512, 1028
gy, gx = 38, 12

mx = 0
my = 0

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
        stack = numpy.zeros(dtype=numpy.uint16, shape=(my * mx, ny, nx))
        frame = data[i][()]
        for j in range(my * mx):
            x = j // my
            y = j % my

            module = frame[
                y * (ny + gy) : y * (ny + gy) + ny, x * (nx + gx) : x * (nx + gx) + nx
            ]
            stack[j] = module

        stack = stack.reshape((my * mx * ny * nx,))
