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
    SynthWrapper() {
        // Adapted from https://github.com/Dewb/Tonic/blob/midi/Demo/Standalone/PolyMIDIDemo/main.cpp
        
        noteNum = synth.addParameter("polyNote", 0.0);
        gate = synth.addParameter("polyGate", 0.0);
        noteVelocity = synth.addParameter("polyVelocity", 0.0);
        voiceNumber = synth.addParameter("polyVoiceNumber", 0.0);

        voiceFreq = Tonic::ControlMidiToFreq().input(noteNum);

        tone = (Tonic::Generator)(noteVelocity * Tonic::SquareWave().freq(voiceFreq) * Tonic::SineWave().freq(50));

        env = Tonic::ADSR()
        .attack(0.04)
        .decay( 0.1 )
        .sustain(0.8)
        .release(0.6)
        .doesSustain(true)
        .trigger(gate);

        filterFreq = voiceFreq * 0.5 + 200;
    
        filter = Tonic::LPF24().Q(1.0 + noteVelocity * 0.02).cutoff( filterFreq );

        synth.setOutputGen((((tone * env) >> filter)));

    }

    void startNote(int midiNote, float amplitude) {
        synth.setParameter("polyNote",static_cast<float>(midiNote)); // Update the midiNote parameter
        synth.setParameter("polyGate",static_cast<float>(1.0f)); 
        synth.setParameter("polyVelocity",static_cast<float>(amplitude)); 
    }

    void stopNote() {
        synth.setParameter("polyGate",static_cast<float>(0.0f)); 
    }

    Tonic::Synth& getSynth() {
        return synth;
    }

private:
    Tonic::Synth synth;
    Tonic::SawtoothWave sawWave; // Changed from RectWave to SawtoothWave
    Tonic::ControlParameter ampParam;
    Tonic::ControlParameter midiNoteParam; // ControlParameter for MIDI note
    Tonic::ControlParameter anxietyControl; // ControlParameter for anxiety

    Tonic::ControlParameter noteNum;
    Tonic::ControlParameter gate;
    Tonic::ControlParameter noteVelocity;
    Tonic::ControlParameter voiceNumber;
    Tonic::ControlGenerator voiceFreq;
    Tonic::Generator tone;
    Tonic::ADSR env;
    Tonic::LPF24 filter;
    Tonic::ControlGenerator filterFreq;
    Tonic::ControlGenerator output;

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
}
