# Collect all source files from common_code/src
file(GLOB COMMON_CODE_SRCS "${CMAKE_SOURCE_DIR}/../common/src/*.cpp")

idf_component_register(
    SRCS
        "main.cpp"
        ${COMMON_CODE_SRCS}
    INCLUDE_DIRS
        "."
        "${CMAKE_SOURCE_DIR}/../common/include"
    REQUIRES mqtt esp_wifi nvs_flash esp_event
)
