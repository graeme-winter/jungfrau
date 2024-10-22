cmake_minimum_required(VERSION 3.20)

project(recompressor_test)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")
set(CMAKE_CXX_STANDARD 23)

find_package(HDF5 REQUIRED)

include_directories(bitshuffle/src bitshuffle/lz4)

add_executable(recompressor_test recompressor_test recompressor_test.cc
               bitshuffle/src/bitshuffle.c
               bitshuffle/lz4/lz4.c
               bitshuffle/src/bitshuffle_core.c
               bitshuffle/src/iochain.c)
target_link_libraries(recompressor_test PRIVATE hdf5::hdf5)
target_compile_options(recompressor_test PRIVATE "-O2")
