# Jungfrau

Preparatory work and planning for setting up the Jungfrau detector. Repository primarily for issue tracking at the moment but some code will find its way in.

## Network Basics

Explore network / UDP [in here](./000-project-network/)

## Compression

Explore bitshuffle, lz4 [in here](./001-project-compression-decompression/) - this is just the initial exploration, which is working out how to use the bitshuffle code from DECTRIS and lz4 on a whole block: needs to be properly framed in the way the HDF5 files are compressed.

Exploring this in more detail by first decompressing a block at a time complete HDF5 chunks from a file [in here](./002-project-recreate-dectris-compression/) - this appears to correctly reproduce the behaviour of DECTRIS compression.
