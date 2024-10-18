#include <bit>
#include <cstring>
#include <iostream>
#include <random>
#include <vector>

#include <hdf5.h>

extern "C" {
#include "bitshuffle.h"
#include "lz4.h"
}

/* decompress_chunk
 * decompress chunk according to the lz4 frame definitions
 * arguments:
 * chunk: compressed data frame
 * size: number of bytes in compressed frame
 */

void decompress_chunk(char *chunk, int size) {
  uint64_t image_size;
  uint32_t block_size, compressed;
  std::memcpy(&image_size, chunk, sizeof(uint64_t));
  std::memcpy(&block_size, chunk + sizeof(uint64_t), sizeof(uint32_t));
  image_size = std::byteswap(image_size);
  block_size = std::byteswap(block_size);
  int blocks = 0, offset = sizeof(uint64_t) + sizeof(uint32_t);
  while (offset < size) {
    std::memcpy(&compressed, chunk + offset, sizeof(uint32_t));
    compressed = std::byteswap(compressed);
    offset += compressed + sizeof(uint32_t);
    blocks ++;
  }

  std::cout << image_size << " " << block_size << " " << blocks << std::endl;
}

int main(int argc, char **argv) {

  if (argc == 1) {
    std::cout << argv[0] << " data_00001.h5" << std::endl;
    return 1;
  }

  hid_t file = H5Fopen(argv[1], H5F_ACC_RDONLY, H5P_DEFAULT);

  if (file < 0) {
    std::cout << argv[1] << " is not a valid HDF5 file" << std::endl;
    return 1;
  }

  hid_t data = H5Dopen(file, "/data", H5P_DEFAULT);
  if (data < 0) {
    H5Fclose(file);
    std::cout << argv[1] << "/data is not a valid HDF5 dataset" << std::endl;
    return 1;
  }

  hid_t dspace = H5Dget_space(data);
  const int ndims = H5Sget_simple_extent_ndims(dspace);

  if (ndims != 3) {
    std::cout << "ndims != 3" << std::endl;
    H5Dclose(data);
    H5Fclose(file);
    return 1;
  }

  hsize_t dims[ndims];
  H5Sget_simple_extent_dims(dspace, dims, NULL);

  int NZ = dims[0];
  int NY = dims[1];
  int NX = dims[2];

  hsize_t max_chunk = 0;

  hsize_t off[ndims];

  for (int j = 1; j < ndims; j++) {
    off[j] = 0;
  }

  for (int nz = 0; nz < NZ; nz++) {
    hsize_t chunk_size = 0;
    off[0] = nz;
    H5Dget_chunk_storage_size(data, off, &chunk_size);
    max_chunk = std::max(max_chunk, chunk_size);
  }

  std::vector<char> chunk(max_chunk);

  for (int nz = 0; nz < NZ; nz++) {
    hsize_t chunk_size = 0;
    uint32_t filter = 0;
    off[0] = nz;
    H5Dget_chunk_storage_size(data, off, &chunk_size);
    H5Dread_chunk(data, H5P_DEFAULT, off, &filter, chunk.data());
    decompress_chunk(chunk.data(), (int)chunk_size);
  }

  return 0;
}
