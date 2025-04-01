#include <RtAudio.h>
#include <pybind11/pybind11.h>
#include <atomic>
#include <cmath>
#include <iostream>

#define _USE_MATH_DEFINES  // Fix for M_PI on Windows
#include <math.h>

#define SAMPLE_RATE 48000
#define BUFFER_SIZE 256

class AudioEngine {
public:
    AudioEngine() : phase(0.0f), frequency(440.0f) {
        dac = new RtAudio();
        if (dac->getDeviceCount() == 0) {
            std::cerr << "No audio devices found!" << std::endl;
            delete dac;
            throw std::runtime_error("No audio device found");
        }

        RtAudio::StreamParameters params;
        params.deviceId = dac->getDefaultOutputDevice();
        params.nChannels = 1;
        unsigned int bufferFrames = BUFFER_SIZE;

        try {
            dac->openStream(&params, nullptr, RTAUDIO_FLOAT32, SAMPLE_RATE, &bufferFrames, &audioCallback, this);
            dac->startStream();
        } catch (const std::exception &e) {  // FIX: Use std::exception
            std::cerr << "RtAudio Error: " << e.what() << std::endl;
            delete dac;
            throw;
        }
    }

    ~AudioEngine() {
        if (dac) {
            if (dac->isStreamOpen()) {
                dac->stopStream();
                dac->closeStream();
            }
            delete dac;
        }
    }

    void setFrequency(float newFreq) {
        frequency.store(newFreq, std::memory_order_relaxed);
    }

private:
    static int audioCallback(void* outputBuffer, void*, unsigned int nFrames, double, RtAudioStreamStatus, void* userData) {
        auto* engine = static_cast<AudioEngine*>(userData);
        auto* buffer = static_cast<float*>(outputBuffer);

        float phaseStep = (2.0f * M_PI * engine->frequency) / SAMPLE_RATE;  // FIX: M_PI is now available

        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] = 0.2f * std::sin(engine->phase);
            engine->phase += phaseStep;
            if (engine->phase > 2.0f * M_PI) engine->phase -= 2.0f * M_PI;
        }

        return 0;
    }

    RtAudio* dac;
    std::atomic<float> frequency;
    float phase;
};

namespace py = pybind11;

PYBIND11_MODULE(audio_engine, m) {
    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())
        .def("setFrequency", &AudioEngine::setFrequency);
}
