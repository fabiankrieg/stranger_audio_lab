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


// Wrapper class for Tonic::Synth
class SynthWrapper {
public:
    SynthWrapper(const std::string& waveform = "SineWave", float attack = 0.04, float decay = 0.1, float sustain = 0.8, float release = 0.6, float baseFilterFreq = 200.0, float filterQ = 1.0) {
        // Add parameters to the synth
        noteNum = synth.addParameter("polyNote", 0.0);
        gate = synth.addParameter("polyGate", 0.0);
        noteVelocity = synth.addParameter("polyVelocity", 0.0);

        // Configure ADSR envelope
        env = Tonic::ADSR()
            .attack(attack)
            .decay(decay)
            .sustain(sustain)
            .release(release)
            .doesSustain(true)
            .trigger(gate);

        // Configure waveform
        voiceFreq = Tonic::ControlMidiToFreq().input(noteNum);
        if (waveform == "SineWave") {
            tone = Tonic::SineWave().freq(voiceFreq);
        } else if (waveform == "SquareWave") {
            tone = Tonic::SquareWave().freq(voiceFreq);
        } else if (waveform == "SawtoothWave") {
            tone = Tonic::SawtoothWave().freq(voiceFreq);
        } else {
            throw std::invalid_argument("Unsupported waveform type");
        }

        // Configure filter
        filterFreq = voiceFreq * 0.5 + baseFilterFreq;
        filter = Tonic::LPF24().Q(filterQ).cutoff(filterFreq);

        // Set output generator
        synth.setOutputGen((tone * env) >> filter);
    }

    void startNote(int midiNote, float amplitude) {
        synth.setParameter("polyNote", static_cast<float>(midiNote));
        synth.setParameter("polyGate", 1.0f);
        synth.setParameter("polyVelocity", amplitude);
    }

    void stopNote() {
        synth.setParameter("polyGate", 0.0f);
    }

    Tonic::Synth& getSynth() {
        return synth;
    }

private:
    Tonic::Synth synth;
    Tonic::ControlParameter noteNum, gate, noteVelocity;
    Tonic::ControlGenerator voiceFreq, filterFreq;
    Tonic::Generator tone;
    Tonic::ADSR env;
    Tonic::LPF24 filter;
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
        .def(py::init<const std::string&, float, float, float, float, float, float>()) // Updated constructor
        .def("startNote", &SynthWrapper::startNote)
        .def("stopNote", &SynthWrapper::stopNote);
}
