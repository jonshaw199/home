# The following lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.5)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Add this at the beginning or in the appropriate section
set(EXTRA_COMPONENT_DIRS ${CMAKE_SOURCE_DIR}/../common_components)

project(dial)
