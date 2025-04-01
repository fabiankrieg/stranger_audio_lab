cmake_minimum_required(VERSION 3.27)
project(AudioEngine)

# Include submodules
add_subdirectory(extern/pybind11)

find_package(Python COMPONENTS Interpreter Development)

# Collect Tonic source files
file(GLOB TONIC_SOURCES ${CMAKE_SOURCE_DIR}/extern/Tonic/src/Tonic/*.cpp)

# Collect RtAudio source files
file(GLOB RTAUDIO_SOURCES ${CMAKE_SOURCE_DIR}/extern/rtaudio/*.cpp)

# Create the library
add_library(audio_engine MODULE audio_engine.cpp ${TONIC_SOURCES} ${RTAUDIO_SOURCES})

# Disable debug suffix for the target
set_target_properties(audio_engine PROPERTIES DEBUG_POSTFIX "")

# Link against required libraries
target_link_libraries(audio_engine PRIVATE
    pybind11::module
)

# Add platform-specific libraries and definitions
if(WIN32)
    target_compile_definitions(audio_engine PRIVATE WIN32 __WINDOWS_DS__)
    target_link_libraries(audio_engine PRIVATE winmm dsound) # Windows Multimedia Library and DirectSound
elseif(APPLE)
    target_link_libraries(audio_engine PRIVATE "-framework CoreAudio" "-framework CoreFoundation")
elseif(UNIX)
    target_link_libraries(audio_engine PRIVATE pthread asound)
endif()

# Add include directories
target_include_directories(audio_engine PRIVATE
    ${CMAKE_SOURCE_DIR}/extern/Tonic/src
    ${CMAKE_SOURCE_DIR}/extern/rtaudio
)

set_target_properties(audio_engine 
PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}" 
SUFFIX "${PYTHON_MODULE_EXTENSION}" 
LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bindings
LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR}/bindings
LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR}/bindings
)
