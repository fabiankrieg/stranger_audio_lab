import sys

# Add bindings directory to the Python path
sys.path.insert(0, "./bindings")

from example_simple_multi_part_song import SimpleMultiPartSong
from stranger_playback import StrangerPlayback
import audio_engine

# Create ControlParameters
control_params = audio_engine.ControlParameters()

# Initialize the SimpleMultiPartSong with ControlParameters and BPM
bpm = 250  # Beats per minute
song = SimpleMultiPartSong(control_params, bpm)

# Initialize playback
playback = StrangerPlayback(song, control_params)

# Start playback
try:
    playback.start_playback()
except KeyboardInterrupt:
    print("Playback interrupted by user.")
    playback.stop_playback()

