set(COMPONENT_ADD_INCLUDEDIRS
    src
    )
file(GLOB SRCS
     src/*.cpp
     src/utility/*.cpp
     )
set(COMPONENT_SRCS ${SRCS})

list(APPEND COMPONENT_REQUIRES M5GFX M5Unified arduino-esp32)

message(STATUS "M5Dial use components = ${COMPONENT_REQUIRES}")

register_component()
