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
#include <unordered_map>

#define _USE_MATH_DEFINES  // Fix for M_PI on Windows
#include <math.h>

#define SAMPLE_RATE 48000
#define BUFFER_SIZE 256


// Base class for Tonic Synth Wrapper
class SynthWrapper {
public:
    SynthWrapper() {
        // Add parameters to the synth
        noteNum = synth.addParameter("polyNote", 0.0);
        gate = synth.addParameter("polyGate", 0.0);
        noteVelocity = synth.addParameter("polyVelocity", 0.0);
    }

    virtual ~SynthWrapper() = default;

    virtual void startNote(int midiNote, float amplitude) {
        synth.setParameter("polyNote", static_cast<float>(midiNote));
        synth.setParameter("polyGate", 1.0f);
        synth.setParameter("polyVelocity", amplitude);
    }

    virtual void stopNote() {
        synth.setParameter("polyGate", 0.0f);
    }

    Tonic::Synth& getSynth() {
        return synth;
    }

protected:
    Tonic::Synth synth;
    Tonic::ControlParameter noteNum, gate, noteVelocity;
};

class ControlParameters {
public:
    void addParameter(const std::string& name, float defaultValue = 0.0f) {
        parameters.emplace_back(name, defaultValue);
    }

    const std::vector<std::pair<std::string, float>>& getParameters() const {
        return parameters;
    }

private:
    std::vector<std::pair<std::string, float>> parameters;
};

// Derived class implementing a simple ADSR filter synth
class TonicSimpleADSRFilterSynth : public SynthWrapper {
public:
    TonicSimpleADSRFilterSynth(const std::string& waveform, ControlParameters& controlParams, const std::string& attackName, const std::string& decayName, float sustain, float release, float baseFilterFreq, float filterQ) {
        // Add parameters to the synth
        for (const auto& param : controlParams.getParameters()) {
            parameters[param.first] = synth.addParameter(param.first, param.second);
        }

        // Get references to the attack and decay parameters
        Tonic::ControlParameter& attackControl = parameters.at(attackName);
        Tonic::ControlParameter& decayControl = parameters.at(decayName);

        // Configure the synth
        configureSynth(waveform, attackControl, decayControl, sustain, release, baseFilterFreq, filterQ);
    }

private:
    void configureSynth(const std::string& waveform, Tonic::ControlGenerator attack, Tonic::ControlGenerator decay, float sustain, float release, float baseFilterFreq, float filterQ) {
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

    Tonic::ControlGenerator voiceFreq, filterFreq;
    Tonic::Generator tone;
    Tonic::ADSR env;
    Tonic::LPF24 filter;
    std::unordered_map<std::string, Tonic::ControlParameter> parameters;
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

    py::class_<SynthWrapper, std::shared_ptr<SynthWrapper>>(m, "SynthWrapper");

    py::class_<TonicSimpleADSRFilterSynth, SynthWrapper, std::shared_ptr<TonicSimpleADSRFilterSynth>>(m, "TonicSimpleADSRFilterSynth")
        .def(py::init<const std::string&, ControlParameters&, const std::string&, const std::string&, float, float, float, float>())
        .def("startNote", &TonicSimpleADSRFilterSynth::startNote)
        .def("stopNote", &TonicSimpleADSRFilterSynth::stopNote);

    py::class_<ControlParameters, std::shared_ptr<ControlParameters>>(m, "ControlParameters")
        .def(py::init<>())
        .def("addParameter", &ControlParameters::addParameter)
        .def("getParameters", &ControlParameters::getParameters, py::return_value_policy::reference);
}
