import argparse
import os
import sys

import h5py
import numpy

modules = ["M420", "M418"]


def extract_gain_map(prefix):

    fout = h5py.File("gain.h5", "w")

    for j, module in enumerate(modules):
        filename = os.path.join(
            f"{prefix}",
            f"{module}_fullspeed",
            f"gainMaps_{module}_fullspeed_2023-01-24.bin",
        )

        shape = 6, 512, 1024
        count = 6 * 512 * 1024

        assert os.path.exists(filename)
        assert os.stat(filename).st_size == 8 * count

        with open(filename, "r") as fin:
            gains = numpy.fromfile(fin, dtype=numpy.float64, count=count).reshape(
                *shape
            )
            g0 = fout.create_group(f"module_{2 * j:02d}")
            for g in range(3):
                data = 1.0 / gains[g, :256, :].astype(numpy.float32)
                g0.create_dataset(
                    f"gain{g}", shape=(256, 1024), dtype=numpy.float32, data=data
                )
            g1 = fout.create_group(f"module_{2 * j + 1:02d}")
            for g in range(3):
                data = 1.0 / gains[g, 256:, :].astype(numpy.float32)
                g1.create_dataset(
                    f"gain{g}", shape=(256, 1024), dtype=numpy.float32, data=data
                )

    fout.close()

def main():
    parser = argparse.ArgumentParser(
        prog="gain_extractor",
        description="Extract gain maps from JUNGFRAU calibration to half modules",
    )
    parser.add_argument("prefix")

    args = parser.parse_args()
    extract_gain_map(args.prefix)


if __name__ == "__main__":
    main()
