#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

#include <nlohmann/json.hpp>
#include <zmq_addon.hpp>

#include <hdf5.h>

extern "C" {
#include "bitshuffle.h"
}

// correction tables
float gain0[256 * 1024];
float gain1[256 * 1024];
float gain2[256 * 1024];
float pedestal0[256 * 1024];
float pedestal1[256 * 1024];
float pedestal2[256 * 1024];

void setup(int module) {
  std::stringstream module_name;
  module_name << "module_" << std::setfill('0') << std::setw(2) << (module % 4);

  hid_t file = H5Fopen("gain.h5", H5F_ACC_RDONLY, H5P_DEFAULT);
  if (file < 0) {
    throw std::invalid_argument("error reading gain.h5");
  }

  hid_t group = H5Gopen(file, module_name.str().c_str(), H5P_DEFAULT);
  if (group < 0) {
    H5Fclose(file);
    throw std::invalid_argument("error opening module group");
  }

  hsize_t offset[2] = {0};
  unsigned int filter;

  hid_t dataset = H5Dopen(group, "gain0", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening gain0 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, gain0);
  H5Dclose(dataset);

  dataset = H5Dopen(group, "gain1", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening gain1 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, gain1);
  H5Dclose(dataset);

  dataset = H5Dopen(group, "gain2", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening gain2 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, gain2);
  H5Dclose(dataset);

  H5Gclose(group);
  H5Fclose(file);

  file = H5Fopen("pedestal.h5", H5F_ACC_RDONLY, H5P_DEFAULT);
  if (file < 0) {
    throw std::invalid_argument("error reading gain.h5");
  }

  group = H5Gopen(file, module_name.str().c_str(), H5P_DEFAULT);
  if (group < 0) {
    H5Fclose(file);
    throw std::invalid_argument("error opening module group");
  }

  dataset = H5Dopen(group, "pedestal0", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening pedestal0 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, pedestal0);
  H5Dclose(dataset);

  dataset = H5Dopen(group, "pedestal1", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening pedestal1 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, pedestal1);
  H5Dclose(dataset);

  dataset = H5Dopen(group, "pedestal2", H5P_DEFAULT);
  if (dataset < 0) {
    H5Gclose(file);
    H5Fclose(file);
    throw std::invalid_argument("error opening pedestal1 dataset");
  }
  H5Dread(dataset, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, pedestal2);
  H5Dclose(dataset);

  H5Gclose(group);
  H5Fclose(file);
}

void correct_image(unsigned short *image) {
  for (int j = 0; j < 256 * 1024; j++) {
    unsigned short corrected = 0x8000;
    short mode = image[j] >> 14;
    float value = (float)(image[j] & 0x3fff);
    if (mode == 0) {
      if (pedestal0[j])
        corrected = rint((value - pedestal0[j]) * gain0[j]);
    } else if (mode == 1) {
      if (pedestal1[j])
        corrected = rint((value - pedestal1[j]) * gain1[j]);
    } else if (mode == 3) {
      if (pedestal2[j])
        corrected = rint((value - pedestal2[j]) * gain2[j]);
    }
    image[j] = corrected;
  }
}

int main(int argc, char **argv) {
  int port = atoi(argv[1]);

  setup(port - 30001);

  float wavelength = atof(argv[2]);
  float scale = wavelength / 12.398425;

  for (int j = 0; j < 256 * 1024; j++) {
    gain0[j] = scale * gain0[j];
    gain1[j] = scale * gain1[j];
    gain2[j] = scale * gain2[j];
  }

  // receiver

  std::stringstream host;
  host << "tcp://127.0.0.1:" << port;

  std::cerr << "Connecting to: " << host.str() << std::endl;

  zmq::context_t ctx;
  zmq::socket_t sock(ctx, zmq::socket_type::sub);

  sock.set(zmq::sockopt::subscribe, "");
  sock.set(zmq::sockopt::rcvhwm, 50000);
  sock.set(zmq::sockopt::rcvbuf, 128 * 1024 * 1024);
  sock.connect(host.str());

  // sender
  std::stringstream out;
  out << "tcp://0.0.0.0:" << port + 10000;

  std::cerr << "Binding to: " << out.str() << std::endl;

  zmq::socket_t send(ctx, zmq::socket_type::push);

  send.set(zmq::sockopt::sndhwm, 50000);
  send.set(zmq::sockopt::sndbuf, 128 * 1024 * 1024);
  send.bind(out.str());

  std::vector<int> found;
  std::vector<int> timestamp;
  std::vector<int> complete;
  std::vector<int> size;

  std::chrono::time_point<std::chrono::high_resolution_clock> t0, t;

  bool configure = false;

  while (true) {
    std::vector<zmq::message_t> recv_msgs;
    const auto ret = zmq::recv_multipart(sock, std::back_inserter(recv_msgs));

    if (!configure) {
      t0 = std::chrono::high_resolution_clock::now();
      configure = true;
    }

    t = std::chrono::high_resolution_clock::now();

    std::string header_str = recv_msgs[0].to_string();

    auto header = nlohmann::json::parse(header_str);

    std::int32_t bitmode = header["bitmode"].template get<std::int32_t>();
    std::int32_t frame = header["frameIndex"].template get<std::int32_t>();

    if (bitmode == 0)
      break;

    unsigned short *image = recv_msgs[1].data<unsigned short>();
    correct_image(image);

    char scratch[2 * 256 * 1024];

    // first 12 bytes are uint64_t BE array size and uint32_t BE block size
    // these are the precomputed values
    unsigned int *alias32 = (unsigned int *)scratch;
    unsigned long long *alias64 = (unsigned long long *)scratch;
    alias64[0] = __builtin_bswap64(2 * 256 * 1024);
    alias32[2] = __builtin_bswap32(8192);

    int _size =
        bshuf_compress_lz4(image, scratch + 12, 256 * 1024, sizeof(short), 4096);

    zmq::multipart_t send_msgs;
    std::vector<int> send_hdr = {frame};
    send_msgs.push_back(zmq::message_t(send_hdr));
    send_msgs.push_back(zmq::message_t(scratch, _size + 12));
    zmq::send_multipart(send, send_msgs);

    size.push_back(_size);

    found.push_back(frame);
    timestamp.push_back(
        std::chrono::duration_cast<std::chrono::microseconds>(t - t0).count());
    complete.push_back(header["completeImage"].template get<std::int32_t>());
  }

  int n = found.size();

  for (int j = 0; j < n; j++)
    std::cout << found[j] << " " << complete[j] << " " << timestamp[j] << " "
              << size[j] << std::endl;

  return 0;
}
