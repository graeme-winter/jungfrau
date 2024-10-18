#include <algorithm>
#include <iostream>
#include <random>
#include <vector>

extern "C" {
#include "bitshuffle.h"
#include "lz4.h"
}

#define NY 512
#define NX 1028

void poisson_image(std::vector<int16_t> &image, float rate) {
  std::random_device device;
  std::mt19937 generator(device());
  std::poisson_distribution<int> distribution(rate);

  for (int i = 0; i < NY; i++) {
    for (int j = 0; j < NX; j++) {
      image[i * NX + j] = (int16_t)distribution(generator);
    }
  }
}

void gaussian_image(std::vector<int16_t> &image, float mean, float sd) {
  std::random_device device;
  std::mt19937 generator(device());
  std::normal_distribution distribution(mean, sd);

  for (int i = 0; i < NY; i++) {
    for (int j = 0; j < NX; j++) {
      image[i * NX + j] = (int16_t)std::round(distribution(generator));
    }
  }
}

int main(int argc, char **argv) {
  std::vector<int16_t> module(NY * NX);

  float rate = 1.0;

  float mean = 1.0;
  float sd = 0.5;

  poisson_image(module, rate);

  std::cout << *std::min_element(module.begin(), module.end()) << " "
            << *std::max_element(module.begin(), module.end()) << std::endl;

  std::vector<char> scratch(NY * NX * sizeof(int16_t));
  std::vector<char> shuffled(NY * NX * sizeof(int16_t));
  std::vector<char> compressed(LZ4_COMPRESSBOUND(NY * NX * sizeof(int16_t)));

  // shuffle - this is shuffling the whole block which is almost certainly wrong
  int shuffle_status =
      bitshuf_encode_block(shuffled.data(), (char *)module.data(),
                           scratch.data(), NY * NX, sizeof(int16_t));

  if (shuffle_status) {
    std::cerr << "shuffle failed: " << shuffle_status << std::endl;
    return 1;
  }

  // lz4 compress - again doing the whole block which is ... wrong
  int lz4_status = LZ4_compress_default(
      shuffled.data(), compressed.data(), NX * NY * sizeof(int16_t),
      LZ4_COMPRESSBOUND(NY * NX * sizeof(int16_t)));

  std::cout << "Original size: " << NX * NY * sizeof(int16_t) << std::endl;
  std::cout << "Compressed size: " << lz4_status << std::endl;

  gaussian_image(module, mean, sd);

  std::cout << *std::min_element(module.begin(), module.end()) << " "
            << *std::max_element(module.begin(), module.end()) << std::endl;

  // shuffle - this is shuffling the whole block which is almost certainly wrong
  shuffle_status =
      bitshuf_encode_block(shuffled.data(), (char *)module.data(),
                           scratch.data(), NY * NX, sizeof(int16_t));

  if (shuffle_status) {
    std::cerr << "shuffle failed: " << shuffle_status << std::endl;
    return 1;
  }

  // lz4 compress - again doing the whole block which is ... wrong
  lz4_status = LZ4_compress_default(
      shuffled.data(), compressed.data(), NX * NY * sizeof(int16_t),
      LZ4_COMPRESSBOUND(NY * NX * sizeof(int16_t)));

  std::cout << "Original size: " << NX * NY * sizeof(int16_t) << std::endl;
  std::cout << "Compressed size: " << lz4_status << std::endl;

  return 0;
}
