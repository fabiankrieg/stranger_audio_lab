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
            noteNum = synth.addParameter("polyNote", 0.0);
            pitchBend = synth.addParameter("pitchBend", 0.0);
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
    
        virtual void updateParameter(const std::string& parameterName, float value) {
            synth.setParameter(parameterName, value);
        }
    
        Tonic::Synth& getSynth() {
            return synth;
        }
    
    protected:
        Tonic::Synth synth;
        Tonic::ControlParameter noteNum, gate, noteVelocity, pitchBend;
    };

// Derived class implementing a simple ADSR filter synth
class TonicSimpleADSRFilterSynth : public SynthWrapper {
    public:
        TonicSimpleADSRFilterSynth(const std::string& waveform, float attack, float decay, float sustain, float release, float baseFilterFreq, float filterQ) {
            configureSynth(waveform, attack, decay, sustain, release, baseFilterFreq, filterQ);
        }
    
    private:
        void configureSynth(const std::string& waveform, float attack, float decay, float sustain, float release, float baseFilterFreq, float filterQ) {
            env = Tonic::ADSR()
                .attack(attack)
                .decay(decay)
                .sustain(sustain)
                .release(release)
                .doesSustain(true)
                .trigger(gate);
    
            voiceFreq = Tonic::ControlMidiToFreq().input(noteNum);
            if (waveform == "SineWave") {
                tone = Tonic::SineWave().freq(voiceFreq + pitchBend);
            } else if (waveform == "SquareWave") {
                tone = Tonic::SquareWave().freq(voiceFreq + pitchBend);
            } else if (waveform == "SawtoothWave") {
                tone = Tonic::SawtoothWave().freq(voiceFreq + pitchBend);
            } else {
                throw std::invalid_argument("Unsupported waveform type");
            }
    
            filterFreq = voiceFreq * 0.5 + baseFilterFreq;
            filter = Tonic::LPF24().Q(filterQ).cutoff(filterFreq);
    
            synth.setOutputGen((tone * env) >> filter);
        }
    
        Tonic::ControlGenerator voiceFreq, filterFreq;
        Tonic::Generator tone;
        Tonic::ADSR env;
        Tonic::LPF24 filter;
    };

class ControlParameters {
public:
    void linkParameter(const std::string& synthName, const std::string& synthParameterName, const std::string& controlParameterName) {
        linkedParameters[controlParameterName].push_back(std::make_pair(synthName, synthParameterName));
    }

    void updateParameter(const std::string& controlParameterName, float value) {
        auto it = linkedParameters.find(controlParameterName);
        if (it != linkedParameters.end()) {
            for (const auto& pair : it->second) {
                const std::string& synthName = pair.first;
                const std::string& synthParameterName = pair.second;
                if (synths.find(synthName) != synths.end()) {
                    synths[synthName]->updateParameter(synthParameterName, value);
                }
            }
        }
    }

    void registerSynth(const std::string& name, std::shared_ptr<SynthWrapper> synth) {
        synths[name] = synth;
    }

private:
    std::unordered_map<std::string, std::vector<std::pair<std::string, std::string>>> linkedParameters; // controlParameterName -> list of (synthName, synthParameterName)
    std::unordered_map<std::string, std::shared_ptr<SynthWrapper>> synths;                              // synthName -> synth instance
};



class AudioEngine {
public:
    AudioEngine(ControlParameters& controlParams) : dac(nullptr), controlParams(controlParams) {}

    ~AudioEngine() {
        stop();
    }

    void start() {
        if (dac) return;

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

    void registerSynth(const std::string& name, std::shared_ptr<SynthWrapper> synth) {
        mixer.addInput(synth->getSynth());
        synths.push_back(synth);
        controlParams.registerSynth(name, synth);
    }

private:
    static int audioCallback(void* outputBuffer, void*, unsigned int nFrames, double, RtAudioStreamStatus, void* userData) {
        auto* engine = static_cast<AudioEngine*>(userData);
        auto* buffer = static_cast<float*>(outputBuffer);

        engine->mixer.fillBufferOfFloats(buffer, nFrames, 1);

        return 0;
    }

    RtAudio* dac;
    Tonic::Mixer mixer;
    std::vector<std::shared_ptr<SynthWrapper>> synths;
    ControlParameters& controlParams;
};

namespace py = pybind11;

PYBIND11_MODULE(audio_engine, m) {
    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<ControlParameters&>())
        .def("start", &AudioEngine::start)
        .def("stop", &AudioEngine::stop)
        .def("registerSynth", &AudioEngine::registerSynth);

    py::class_<SynthWrapper, std::shared_ptr<SynthWrapper>>(m, "SynthWrapper");

    py::class_<TonicSimpleADSRFilterSynth, SynthWrapper, std::shared_ptr<TonicSimpleADSRFilterSynth>>(m, "TonicSimpleADSRFilterSynth")
        .def(py::init<const std::string&, float, float, float, float, float, float>())
        .def("startNote", &TonicSimpleADSRFilterSynth::startNote)
        .def("stopNote", &TonicSimpleADSRFilterSynth::stopNote);

    py::class_<ControlParameters, std::shared_ptr<ControlParameters>>(m, "ControlParameters")
        .def(py::init<>())
        .def("linkParameter", &ControlParameters::linkParameter)
        .def("updateParameter", &ControlParameters::updateParameter);
}
