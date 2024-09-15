# Minimum required CMake version
cmake_minimum_required(VERSION 3.5)

# Include ESP-IDF's CMake project script
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Set the additional component directories
set(EXTRA_COMPONENT_DIRS ${CMAKE_SOURCE_DIR}/../common_components)

# Define the project
project(environmental)
