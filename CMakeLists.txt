cmake_minimum_required(VERSION 3.27)
project(AudioEngine)

# Include stuff that we carry over in submodules
add_subdirectory(extern/pybind11)
add_subdirectory(extern/JUCE)

find_package(Python COMPONENTS Interpreter Development)

# link our great file
add_library(audio_engine MODULE audio_engine.cpp)
target_link_libraries(audio_engine PRIVATE
juce::juce_audio_basics
juce::juce_audio_devices
pybind11::module)
