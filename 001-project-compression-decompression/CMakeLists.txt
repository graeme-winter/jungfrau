cmake_minimum_required(VERSION 3.20)

project(compressor_test)

set(CMAKE_CXX_STANDARD 17)

include_directories(bitshuffle/src lz4/lib)

add_executable(compressor_test compressor_test compressor_test.cc
               bitshuffle/src/bitshuffle.c
               lz4/lib/lz4.c)
target_compile_options(compressor_test PRIVATE "-O2")
