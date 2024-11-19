import sys

import h5py
import hdf5plugin
import numpy
import tqdm

ny, nx = 512, 1028
gy, gx = 38, 12

mx = 0
my = 0

# hard coded for i04-1 - it'll do

G0E = 40 * 13.504
G1E = -1.5 * 13.504
G2E = -0.1 * 13.504

P0 = 3000
P1 = 15000
P2 = 15000


def count_to_adc(stack):
    """Convert counts back to ADC readouts and gain mode"""
    mask = stack < 0xFFFE
    stack *= mask
    g0 = (stack >= 0) & (stack < 25)
    g1 = (stack >= 25) & (stack < 700)
    g2 = stack >= 700
    result = (
        (stack * g0 * G0E + g0 * P0)
        + (stack * g1 * G1E + g1 * P1)
        + (stack * g2 * G2E + g2 * P2)
    ).astype(numpy.uint16)
    result += (g1 * (1 << 14) + g2 * (3 << 14)).astype(numpy.uint16)
    result = mask * result
    return result


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

    fouts = [
        open(f"{sys.argv[2]}/stream_{j:02d}.raw", "wb") for j in range(my * mx * 2)
    ]

    for i in tqdm.tqdm(range(data.shape[0])):
        header = numpy.zeros((14,), dtype=numpy.uint64)
        header[0] = i
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

        # reshape into half-modules
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

    for fout in fouts:
        fout.close()
