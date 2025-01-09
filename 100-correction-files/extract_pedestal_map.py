import argparse
import os

import numpy
import h5py
import tqdm

GAIN_MODES = 0, 1, 3


def extract_pedestal_map(prefix):
    for g in range(3):
        for j in range(4):
            assert os.path.exists(os.path.join(prefix, f"G{g}_{j}_0.h5"))

    fins = {}
    for g in range(3):
        for j in range(4):
            fins[g, j] = h5py.File(os.path.join(prefix, f"G{g}_{j}_0.h5"), "r")

    fout = h5py.File("pedestal.h5", "w")

    dins = {}

    for key in fins:
        dins[key] = fins[key]["data"]

    for key in dins:
        assert dins[key].shape == dins[(0, 0)].shape

    for key in dins:
        gain, module = key
        if not f"module_{module:02d}" in fout:
            ped = fout.create_group(f"module_{module:02d}")
        else:
            ped = fout[f"module_{module:02d}"]
        din = dins[key]
        valid = numpy.zeros(shape=din.shape[1:], dtype=numpy.int32)
        total = numpy.zeros(shape=din.shape[1:], dtype=numpy.float64)
        for j in tqdm.tqdm(range(din.shape[0])):
            frame = din[j]
            mode = frame >> 14
            mask = mode == GAIN_MODES[gain]
            valid += mask
            total += (frame & 0x3FFF) * mask
        valid[total == 0] = 1
        data = (total / valid).astype(numpy.float32)
        ped.create_dataset(
            f"pedestal{gain}", shape=(256, 1024), dtype=numpy.float32, data=data
        )

    for key in fins:
        fins[key].close()

    fout.close()


def main():
    parser = argparse.ArgumentParser(
        prog="pedestal",
        description="Compute pedestal values from dark run files",
    )
    parser.add_argument("prefix")

    args = parser.parse_args()

    extract_pedestal_map(args.prefix)


if __name__ == "__main__":
    main()
