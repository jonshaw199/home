# Minimum required CMake version
cmake_minimum_required(VERSION 3.5)

# Include ESP-IDF's CMake project script
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Set the additional component directories
set(EXTRA_COMPONENT_DIRS ${CMAKE_SOURCE_DIR}/../common_components)

# Define the partition table files
set(PARTITION_TABLE_CSV "partitions.csv")

# Define the project
project(dial)

# Create the SPIFFS partition image
# The partition label should match the label used in your partitions.csv file
#spiffs_create_partition_image(storage ${CMAKE_SOURCE_DIR}/data)

# Add dependencies if needed
spiffs_create_partition_image(storage ${CMAKE_SOURCE_DIR}/data FLASH_IN_PROJECT)
