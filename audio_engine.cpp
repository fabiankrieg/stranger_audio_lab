#include <juce_audio_utils/juce_audio_utils.h>  
#include <juce_audio_devices/juce_audio_devices.h>
#include <juce_audio_basics/juce_audio_basics.h>
#include <pybind11/pybind11.h>


class SimpleSynth
{
public:
    void setFrequency(float newFrequency, double sampleRate)
    {
        frequency = newFrequency;
        phaseDelta = juce::MathConstants<double>::twoPi * frequency / sampleRate;
    }
    
    float getNextSample()
    {
        float sample = std::sin(phase) * 0.2f;
        phase += phaseDelta;
        if(phase >= juce::MathConstants<double>::twoPi)
            phase -= juce::MathConstants<double>::twoPi;
           
        return sample;
    }
    
private:
    double phase = 0.0;
    double phaseDelta = 0.0;
    float frequency = 440.0f;
};

class AudioEngine : public juce::AudioAppComponent
{
public:
    AudioEngine() {
        setAudioChannels(0, 2);
    }

    ~AudioEngine() {
        shutdownAudio();
    }

    void prepareToPlay(int samplesPerBlockExpected, double sampleRate) override {
        this->currentSampleRate = sampleRate;  // Store sample rate for later use
        osc.setFrequency(frequency, currentSampleRate);
    }

    void getNextAudioBlock(const juce::AudioSourceChannelInfo& bufferToFill) override {
        for (int channel = 0; channel < bufferToFill.buffer->getNumChannels(); ++channel) {
            auto* buffer = bufferToFill.buffer->getWritePointer(channel, bufferToFill.startSample);
            for (int sample = 0; sample < bufferToFill.numSamples; ++sample)
                buffer[sample] = osc.getNextSample();
        }
    }

    void releaseResources() override {}

    void setFrequency(float newFrequency) {
        frequency = newFrequency;
        if (currentSampleRate > 0)  // Ensure we have a valid sample rate
            osc.setFrequency(frequency, currentSampleRate);
    }

    double getStoredSampleRate() const {
        return currentSampleRate;
    }

private:
    float frequency = 440.0f;
    double currentSampleRate = 0.0;  // Store the sample rate
    SimpleSynth osc;
};


namespace py = pybind11;
PYBIND11_MODULE(audio_engine, m)
{
    py::class_<AudioEngine>(m, "AudioEngine")
        .def(py::init<>())
        .def("setFrequency", &AudioEngine::setFrequency);
}