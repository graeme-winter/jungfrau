# raw - make raw data files from HDF5 files which have the half-modules split
# out - this will need to interleave the half modules - beware this will be
# very hard coded...

import sys

import h5py
import tqdm


def main(filenames):
    assert len(filenames) == 4
    datasets = [h5py.File(filename)["data"] for filename in filenames]

    frames = datasets[0].shape[0]

    fouts = [open(f"module_{row}_0.raw", "wb") for row in (0, 2)]

    for j in tqdm.tqdm(range(frames)):
        mod0 = datasets[0][j].tobytes()
        fouts[0].write(mod0)
        mod1 = datasets[1][j].tobytes()
        fouts[0].write(mod1)
        mod2 = datasets[2][j].tobytes()
        fouts[1].write(mod2)
        mod3 = datasets[3][j].tobytes()
        fouts[1].write(mod3)

    for fout in fouts:
        fout.close()


main(sys.argv[1:])
