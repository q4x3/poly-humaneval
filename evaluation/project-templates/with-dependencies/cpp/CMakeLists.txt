cmake_minimum_required(VERSION 3.25)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})

project(test)

find_package(OpenSSL REQUIRED)

add_executable(test src/main.cpp src/target.h src/target.cpp src/utils/utils.h src/utils/utils.cpp)

target_link_libraries(test openssl::openssl)