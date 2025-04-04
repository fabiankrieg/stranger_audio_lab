#include <RtAudio.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <atomic>
#include <cmath>
#include <iostream>
#include <vector>
#include <memory>
#include <Tonic.h>
#include <mutex>

#define _USE_MATH_DEFINES  // Fix for M_PI on Windows
#include <math.h>

#define SAMPLE_RATE 48000
#define BUFFER_SIZE 256

// Singleton class for global control parameters
class ControlParameters {
public:
    static ControlParameters& getInstance() {
        static ControlParameters instance;
        return instance;
    }

    void setAnxiety(float value) {
        std::lock_guard<std::mutex> lock(mutex);
        anxiety = std::min(std::max(value, 0.0f), 1.0f); // Ensure value is in range [0, 1]
        for (auto& callback : anxietyCallbacks) {
            callback(anxiety);
        }
    }

    float getAnxiety() {
        std::lock_guard<std::mutex> lock(mutex);
        return anxiety;
    }

    void registerAnxietyCallback(const std::function<void(float)>& callback) {
        std::lock_guard<std::mutex> lock(mutex);
        anxietyCallbacks.push_back(callback);
    }

private:
    ControlParameters() : anxiety(0.0f) {} // Default anxiety value
    ControlParameters(const ControlParameters&) = delete;
    ControlParameters& operator=(const ControlParameters&) = delete;

    float anxiety;
    std::mutex mutex;
    std::vector<std::function<void(float)>> anxietyCallbacks; // List of callbacks for anxiety changes
};

// Wrapper class for Tonic::Synth
class SynthWrapper {
public:
    SynthWrapper() {
        ampParam = synth.addParameter("amp");
        sawWave = Tonic::SawtoothWave();
        sawWave.freq(440.0f); // Default frequency

        // Add BitCrusher effect controlled by anxiety
        Tonic::BitCrusher bitCrusher;
        bitCrusher.input(sawWave * ampParam);

        // Use ControlParameter for anxiety
        anxietyControl = synth.addParameter("anxiety");
        bitCrusher.bitDepth(Tonic::ControlValue(256) - anxietyControl * 255);

        synth.setOutputGen(bitCrusher);

        // Register callback to update anxietyControl
        ControlParameters::getInstance().registerAnxietyCallback([this, &bitCrusher](float value) {
            anxietyControl.setNormalizedValue(value);
            bitCrusher.bitDepth(Tonic::ControlValue(256) - anxietyControl * 255);
        });
    }

    void startNote(int midiNote, float amplitude) {
        Tonic::ControlMidiToFreq midiToFreq = Tonic::ControlMidiToFreq().input(Tonic::ControlValue(midiNote));
        sawWave.freq(midiToFreq);
        ampParam.setNormalizedValue(amplitude);
    }

    void stopNote() {
        ampParam.setNormalizedValue(0.0f); // Gradually reduce amplitude to stop the note
    }

    Tonic::Synth& getSynth() {
        return synth;
    }

private:
    Tonic::Synth synth;
    Tonic::SawtoothWave sawWave; // Changed from RectWave to SawtoothWave
    Tonic::ControlParameter ampParam;
    Tonic::ControlParameter anxietyControl; // ControlParameter for anxiety
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

    void registerSynth(std::shared_ptr<SynthWrapper> synth) {
        mixer.addInput(synth->getSynth());
        synths.push_back(synth);
    }

private:
    static int audioCallback(void* outputBuffer, void*, unsigned int nFrames, double, RtAudioStreamStatus, void* userData) {
        auto* engine = static_cast<AudioEngine*>(userData);
        auto* buffer = static_cast<float*>(outputBuffer);

        // Use the mixer to fill the buffer with mixed audio
        engine->mixer.fillBufferOfFloats(buffer, nFrames, 1);

        return 0;
    }

    RtAudio* dac;
    Tonic::Mixer mixer; // Mixer to combine signals from all synths
    std::vector<std::shared_ptr<SynthWrapper>> synths; // Store multiple SynthWrapper instances
};

namespace py = pybind11;

PYBIND11_MODULE(audio_engine, m) {
    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())
        .def("start", &AudioEngine::start)
        .def("stop", &AudioEngine::stop)
        .def("registerSynth", &AudioEngine::registerSynth);

    py::class_<SynthWrapper, std::shared_ptr<SynthWrapper>>(m, "SynthWrapper")
        .def(py::init<>())
        .def("startNote", &SynthWrapper::startNote)
        .def("stopNote", &SynthWrapper::stopNote);

    py::class_<ControlParameters>(m, "ControlParameters")
        .def_static("getInstance", &ControlParameters::getInstance, py::return_value_policy::reference)
        .def("setAnxiety", &ControlParameters::setAnxiety)
        .def("getAnxiety", &ControlParameters::getAnxiety);
}
