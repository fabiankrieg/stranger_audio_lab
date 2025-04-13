# stranger_audio_lab

> For the ones who dream of stranger worlds


Let's build some strange audio procedurally which spooks us well.


## How to get started

Best to download [VSCode](https://code.visualstudio.com/) and follow the [MSVC++ FAQ](https://code.visualstudio.com/docs/cpp/config-msvc). We also use CMake, so get [the CMake extension](https://marketplace.visualstudio.com/items/?itemName=ms-vscode.cmake-tools). [Here](https://code.visualstudio.com/docs/cpp/cmake-quickstart) is a small getting started but basically you will need to set the Generator to something with `AMD64 cl.exe`.

Also, after installing VSCode and MSVC Build toos but before everything else - do not forget to start the Developer Command Prompt and start VSCode from that - otherwise it won't find your compiler and stuff.

After all that is done Compile the C-Code and start the `main.py` to hear some first sounds :)


## Dependencies

This project uses the following open-source libraries via Git submodules:

- [RTaudio](https://github.com/thestk/rtaudio) – MIT License
- [PyBind11](https://github.com/pybind/pybind11) – BSD License
- [Tonic](https://github.com/TonicAudio/Tonic) – Unlicense

Please see the respective repositories for full license terms.