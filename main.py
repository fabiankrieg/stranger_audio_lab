import sys

# Add bindings directory to the Python path
sys.path.insert(0, "./bindings")

from example_simple_multi_part_song import SimpleMultiPartSong
from stranger_playback import StrangerPlayback
import audio_engine
from time import sleep

# Create ControlParameters
control_params = audio_engine.ControlParameters()

# Initialize the SimpleMultiPartSong with ControlParameters and BPM
bpm = 250  # Beats per minute
song = SimpleMultiPartSong(control_params, bpm)

synths = song.get_synthesizers()
for synth_name, synth in synths.items():
    control_params.linkParameter(synth_name, "pitchBend", "pitchBend")
    
# Initialize playback
playback = StrangerPlayback(song, control_params)

current_pitch_bend = 0
# Start playback
try:
    control_params.updateParameter("pitchBend", current_pitch_bend)
    current_pitch_bend += 1
    if current_pitch_bend > 127:
        current_pitch_bend = 0
    print(f"Current pitch bend: {current_pitch_bend}")
    playback.start_playback()
except KeyboardInterrupt:
    print("Playback interrupted by user.")
    playback.stop_playback()

