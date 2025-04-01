cmake_minimum_required(VERSION 3.27)
project(AudioEngine)

# Include submodules
add_subdirectory(extern/pybind11)
add_subdirectory(extern/JUCE)

find_package(Python COMPONENTS Interpreter Development)

# Create the library
add_library(audio_engine MODULE audio_engine.cpp)

# Link against the required JUCE modules
target_link_libraries(audio_engine PRIVATE
    juce::juce_audio_basics
    juce::juce_audio_devices
    juce::juce_audio_utils
    pybind11::module
)

# Add JUCE include directories
target_include_directories(audio_engine PRIVATE
    ${CMAKE_SOURCE_DIR}/extern/JUCE/modules
)
