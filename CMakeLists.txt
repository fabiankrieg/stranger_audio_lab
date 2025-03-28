cmake_minimum_required(VERSION 3.15)
project(AudioEngine)

find_package(pybind11 REQUIRED)
add_subdirectory(JUCE)

add_library(audio_engine MODULE audio_engine.cpp)
target_link_libraries(audio_engine PRIVATE
juce::juce_audio_basics
juce::juce_audio_devices
pybind11::module)
