#include <iostream>
#include <random>
#include <vector>

extern "C" {
#include "bitshuffle.h"
#include "lz4.h"
}

#define NY 512
#define NX 1028

void random_image(std::vector<uint16_t> &image, float rate) {
  std::random_device device;
  std::mt19937 generator(device());
  std::poisson_distribution<int> distribution(rate);

  for (int i = 0; i < NY; i++) {
    for (int j = 0; j < NX; j++) {
      image[i * NX + j] = (uint16_t)distribution(generator);
    }
  }
}

int main(int argc, char **argv) {
  std::vector<uint16_t> module(NY * NX);

  float rate = 1.0;

  if (argc > 1) {
    rate = atof(argv[1]);
  }

  random_image(module, rate);

  std::vector<char> scratch(NY * NX * sizeof(uint16_t));
  std::vector<char> shuffled(NY * NX * sizeof(uint16_t));
  std::vector<char> compressed(LZ4_COMPRESSBOUND(NY * NX * sizeof(uint16_t)));

  // shuffle - this is shuffling the whole block which is almost certainly wrong
  int shuffle_status =
      bitshuf_encode_block(shuffled.data(), (char *)module.data(),
                           scratch.data(), NY * NX, sizeof(uint16_t));

  if (shuffle_status) {
    std::cerr << "shuffle failed: " << shuffle_status << std::endl;
    return 1;
  }

  // lz4 compress - again doing the whole block which is ... wrong
  int lz4_status = LZ4_compress_default(
      shuffled.data(), compressed.data(), NX * NY * sizeof(uint16_t),
      LZ4_COMPRESSBOUND(NY * NX * sizeof(uint16_t)));

  std::cout << "Original size: " << NX * NY * sizeof(uint16_t) << std::endl;
  std::cout << "Compressed size: " << lz4_status << std::endl;

  return 0;
}
