#include <RtAudio.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <atomic>
#include <cmath>
#include <iostream>
#include <vector>
#include <memory>
#include <Tonic.h>

#define _USE_MATH_DEFINES  // Fix for M_PI on Windows
#include <math.h>

#define SAMPLE_RATE 48000
#define BUFFER_SIZE 256

class SimpleSynth {
public:
    virtual ~SimpleSynth() = default;

    void setFrequency(float newFreq) {
        frequency.store(newFreq, std::memory_order_relaxed);
    }

    void setFallOff(float newFallOffTimeMs) {
        fallOffTimeMs.store(newFallOffTimeMs, std::memory_order_relaxed);
    }

    void noteOn() {
        amplitude.store(1.0f, std::memory_order_relaxed); // Start playback at full amplitude
        isOn.store(true, std::memory_order_relaxed);      // Set state to "on"
    }

    void noteOff() {
        isOn.store(false, std::memory_order_relaxed);     // Set state to "off"
    }

    void generateBlock(float* buffer, unsigned int nFrames) {
        float currentAmplitude = amplitude.load(std::memory_order_relaxed);
        float fallOffRate = 1.0f / (fallOffTimeMs.load(std::memory_order_relaxed) / 1000.0f * SAMPLE_RATE); // Linear decay per sample
        bool synthIsOn = isOn.load(std::memory_order_relaxed);

        // Generate audio for the sample window
        generateSamples(buffer, nFrames);

        // Apply amplitude and fall-off
        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] *= currentAmplitude * 0.2f;

            // Gradually reduce amplitude only if the synth is "off"
            if (!synthIsOn && currentAmplitude > 0.0f) {
                currentAmplitude -= fallOffRate;
                if (currentAmplitude < 0.0f) currentAmplitude = 0.0f; // Stop completely if it goes below zero
            }
        }

        amplitude.store(currentAmplitude, std::memory_order_relaxed);
    }

protected:
    virtual void generateSamples(float* buffer, unsigned int nFrames) = 0; // Pure virtual function for generating a block of samples

    std::atomic<float> frequency{440.0f};
    std::atomic<float> amplitude{0.0f}; // Current amplitude of the synth
    std::atomic<float> fallOffTimeMs{1000.0f}; // Fall-off time in milliseconds
    std::atomic<bool> isOn{false};       // Tracks whether the synth is "on" or "off"
    float phase{0.0f};
};

class SineSynth : public SimpleSynth {
protected:
    void generateSamples(float* buffer, unsigned int nFrames) override {
        float phaseStep = (2.0f * M_PI * frequency.load(std::memory_order_relaxed)) / SAMPLE_RATE;

        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] = std::sin(phase);
            phase += phaseStep;
            if (phase > 2.0f * M_PI) phase -= 2.0f * M_PI;
        }
    }
};

class SquareSynth : public SimpleSynth {
protected:
    void generateSamples(float* buffer, unsigned int nFrames) override {
        float phaseStep = (2.0f * M_PI * frequency.load(std::memory_order_relaxed)) / SAMPLE_RATE;

        for (unsigned int i = 0; i < nFrames; i++) {
            buffer[i] = (phase < M_PI) ? 1.0f : -1.0f;
            phase += phaseStep;
            if (phase > 2.0f * M_PI) phase -= 2.0f * M_PI;
        }
    }
};

class TonicSquareSynth : public SimpleSynth {
public:
    TonicSquareSynth() {
        generator = Tonic::RectWave();
        synth.setOutputGen(generator);
    }

protected:
    void generateSamples(float* buffer, unsigned int nFrames) override {
        generator.freq(frequency.load(std::memory_order_relaxed)); // Update frequency
        synth.fillBufferOfFloats(buffer, nFrames, 1); // Generate a block of samples
    }

private:
    Tonic::RectWave generator; // Tonic square wave generator
    Tonic::Synth synth;        // Tonic synth to manage the generator
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

        // Let each synth add its output to the buffer
        for (const auto& synth : engine->synths) {
            synth->generateBlock(buffer, nFrames);
        }

        return 0;
    }

    RtAudio* dac;
    std::vector<std::shared_ptr<SimpleSynth>> synths; // Store multiple synthesizers
};

namespace py = pybind11;

PYBIND11_MODULE(audio_engine, m) {
    py::class_<SimpleSynth, std::shared_ptr<SimpleSynth>>(m, "SimpleSynth")
        .def("setFrequency", &SimpleSynth::setFrequency)
        .def("setFallOff", &SimpleSynth::setFallOff)
        .def("noteOn", &SimpleSynth::noteOn)
        .def("noteOff", &SimpleSynth::noteOff);

    py::class_<SineSynth, SimpleSynth, std::shared_ptr<SineSynth>>(m, "SineSynth")
        .def(py::init<>());

    py::class_<SquareSynth, SimpleSynth, std::shared_ptr<SquareSynth>>(m, "SquareSynth")
        .def(py::init<>());

    py::class_<TonicSquareSynth, SimpleSynth, std::shared_ptr<TonicSquareSynth>>(m, "TonicSquareSynth")
        .def(py::init<>());

    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())
        .def("start", &AudioEngine::start)
        .def("stop", &AudioEngine::stop)
        .def("registerSynth", &AudioEngine::registerSynth);
}
