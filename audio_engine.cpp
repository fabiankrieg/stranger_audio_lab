#include <RtAudio.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <atomic>
#include <cmath>
#include <iostream>
#include <vector>
#include <memory>

#define _USE_MATH_DEFINES  // Fix for M_PI on Windows
#include <math.h>

#define SAMPLE_RATE 48000
#define BUFFER_SIZE 256

class SimpleSynth {
public:
    SimpleSynth() : frequency(440.0f), phase(0.0f) {}

    void setFrequency(float newFreq) {
        frequency.store(newFreq, std::memory_order_relaxed);
    }

    void generateBlock(float* buffer, unsigned int nFrames) {
        float phaseStep = (2.0f * M_PI * frequency.load(std::memory_order_relaxed)) / SAMPLE_RATE;

        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] = 0.2f * std::sin(phase); // Generate values for this synth
            phase += phaseStep;
            if (phase > 2.0f * M_PI) phase -= 2.0f * M_PI;
        }
    }

private:
    std::atomic<float> frequency;
    float phase;
};

class AudioEngine {
public:
    AudioEngine() : dac(nullptr) {}

    ~AudioEngine() {
        stop();
    }

    void start() {
        if (dac) return; // Already running

        dac = new RtAudio();
        if (dac->getDeviceCount() == 0) {
            std::cerr << "No audio devices found!" << std::endl;
            delete dac;
            dac = nullptr;
            throw std::runtime_error("No audio device found");
        }

        RtAudio::StreamParameters params;
        params.deviceId = dac->getDefaultOutputDevice();
        params.nChannels = 1;
        unsigned int bufferFrames = BUFFER_SIZE;

        try {
            dac->openStream(&params, nullptr, RTAUDIO_FLOAT32, SAMPLE_RATE, &bufferFrames, &audioCallback, this);
            dac->startStream();
        } catch (const std::exception& e) {
            std::cerr << "RtAudio Error: " << e.what() << std::endl;
            delete dac;
            dac = nullptr;
            throw;
        }
    }

    void stop() {
        if (dac) {
            if (dac->isStreamOpen()) {
                dac->stopStream();
                dac->closeStream();
            }
            delete dac;
            dac = nullptr;
        }
    }

    void registerSynth(std::shared_ptr<SimpleSynth> synth) {
        synths.push_back(synth);
    }

private:
    static int audioCallback(void* outputBuffer, void*, unsigned int nFrames, double, RtAudioStreamStatus, void* userData) {
        auto* engine = static_cast<AudioEngine*>(userData);
        auto* buffer = static_cast<float*>(outputBuffer);

        // Clear the buffer
        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] = 0.0f;
        }

        // Temporary buffer for each synth
        std::vector<float> tempBuffer(nFrames, 0.0f);

        // Mix all registered synthesizers
        for (const auto& synth : engine->synths) {
            synth->generateBlock(tempBuffer.data(), nFrames);
            for (unsigned int i = 0; i < nFrames; i++) {
                buffer[i] += tempBuffer[i]; // Sum the values from all synths
            }
        }

        return 0;
    }

    RtAudio* dac;
    std::vector<std::shared_ptr<SimpleSynth>> synths; // Store multiple synthesizers
};

namespace py = pybind11;

PYBIND11_MODULE(audio_engine, m) {
    py::class_<SimpleSynth, std::shared_ptr<SimpleSynth>>(m, "SimpleSynth")
        .def(py::init<>())
        .def("setFrequency", &SimpleSynth::setFrequency);

    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())
        .def("start", &AudioEngine::start)
        .def("stop", &AudioEngine::stop)
        .def("registerSynth", &AudioEngine::registerSynth);
}
