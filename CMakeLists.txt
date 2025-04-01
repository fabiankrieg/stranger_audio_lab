cmake_minimum_required(VERSION 3.27)
project(AudioEngine)

# Include submodules
add_subdirectory(extern/pybind11)
add_subdirectory(extern/JUCE)

find_package(Python COMPONENTS Interpreter Development)

# Create the library
add_library(audio_engine MODULE audio_engine.cpp)

# Ensure JUCE and Pybind11 are linked correctly
target_link_libraries(audio_engine PRIVATE
    juce::juce_audio_basics
    juce::juce_audio_devices
    pybind11::module
)

# Add JUCE include directories
target_include_directories(audio_engine PRIVATE
    ${CMAKE_SOURCE_DIR}/extern/JUCE/modules
)
