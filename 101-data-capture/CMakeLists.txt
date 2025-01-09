cmake_minimum_required(VERSION 3.20)

if (CMAKE_VERSION VERSION_GREATER_EQUAL "3.24.0")
  cmake_policy(SET CMP0135 NEW)
endif()

project(zeromq_jungfrau_correct)

# fetch dependencies
include(FetchContent)
FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz)
FetchContent_MakeAvailable(json)

set(CMAKE_CXX_STANDARD 17)

find_package(ZeroMQ)
find_package(HDF5 REQUIRED)

include_directories(bitshuffle/src bitshuffle/lz4)

add_executable(zeromq_jungfrau_correct zeromq_jungfrau_correct.cc
               bitshuffle/src/bitshuffle.c
               bitshuffle/lz4/lz4.c
               bitshuffle/src/bitshuffle_core.c
               bitshuffle/src/iochain.c)
target_compile_options(zeromq_jungfrau_correct PRIVATE "-O2")
target_link_libraries(zeromq_jungfrau_correct zmq)
target_link_libraries(zeromq_jungfrau_correct nlohmann_json::nlohmann_json)
target_link_libraries(zeromq_jungfrau_correct hdf5::hdf5)

add_executable(hdf5_jungfrau_correct hdf5_jungfrau_correct.cc)
target_compile_options(hdf5_jungfrau_correct PRIVATE "-O2")
target_link_libraries(hdf5_jungfrau_correct PRIVATE hdf5::hdf5)
