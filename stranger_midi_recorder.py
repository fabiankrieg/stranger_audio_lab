from datetime import datetime
from mido import Message, MidiFile, MidiTrack, MetaMessage, second2tick
import time


class StrangerMidiRecorder:
    """
    A class to handle MIDI recording for a song.

    Attributes:
        _midi_file (MidiFile): The MIDI file to record notes.
        _midi_track (MidiTrack): The MIDI track to store note events.
        _last_event_time (float): The timestamp of the last MIDI event.
        _synth_channels (dict): A mapping of synthesizer names to unique MIDI channels.
        _next_channel (int): The next available MIDI channel.
        _ticks_per_beat (int): The number of ticks per beat in the MIDI file.
        _tempo (int): The tempo in microseconds per beat.
    """

    def __init__(self, bpm):
        """
        Initializes the StrangerMidiRecorder with the song's BPM.

        Args:
            bpm (float): The beats per minute of the song.
        """
        self._ticks_per_beat = 480  # Standard ticks per beat for compatibility with most players
        self._midi_file = MidiFile(ticks_per_beat=self._ticks_per_beat)
        self._midi_track = MidiTrack()
        self._midi_file.tracks.append(self._midi_track)
        self._last_event_time = None  # Initialize to None to handle the first event
        self._synth_channels = {}
        self._next_channel = 0  # MIDI channels range from 0 to 15
        self._tempo = int(60_000_000 / bpm)  # Convert BPM to microseconds per beat

        # Set the tempo in the MIDI file
        self._midi_track.append(MetaMessage('set_tempo', tempo=self._tempo))

    def _get_channel(self, synth_name):
        """
        Retrieves or assigns a unique MIDI channel for a synthesizer.

        Args:
            synth_name (str): The name of the synthesizer.

        Returns:
            int: The assigned MIDI channel.
        """
        if synth_name not in self._synth_channels:
            if self._next_channel > 15:
                raise ValueError("Exceeded the maximum number of MIDI channels (16).")
            self._synth_channels[synth_name] = self._next_channel
            self._next_channel += 1
        return self._synth_channels[synth_name]

    def record_note_on(self, synth_name, pitch, amplitude):
        """
        Records a note-on event in the MIDI track.

        Args:
            synth_name (str): The name of the synthesizer.
            pitch (int): The MIDI pitch of the note.
            amplitude (float): The amplitude of the note (converted to velocity).
        """
        elapsed_time = self._get_elapsed_time()
        midi_time = self._calculate_midi_time(elapsed_time)

        channel = self._get_channel(synth_name)
        velocity = int(amplitude * 127)  # Convert amplitude to MIDI velocity
        self._midi_track.append(Message('note_on', note=pitch, velocity=velocity, time=midi_time, channel=channel))

    def record_note_off(self, synth_name, pitch):
        """
        Records a note-off event in the MIDI track.

        Args:
            synth_name (str): The name of the synthesizer.
            pitch (int): The MIDI pitch of the note.
        """
        elapsed_time = self._get_elapsed_time()
        midi_time = self._calculate_midi_time(elapsed_time)

        channel = self._get_channel(synth_name)
        self._midi_track.append(Message('note_off', note=pitch, velocity=0, time=midi_time, channel=channel))

    def save(self, class_name):
        """
        Saves the MIDI file with a unique filename based on the class name and current date-time.

        Args:
            class_name (str): The name of the song's class.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{class_name}_{timestamp}.mid"
        self._midi_file.save(filename)
        print(f"MIDI file saved as {filename}.")

    def _get_elapsed_time(self):
        """
        Calculates the elapsed time since the last event.

        Returns:
            float: The elapsed time in seconds.
        """
        current_time = time.time()
        if self._last_event_time is None:
            self._last_event_time = current_time
            return 0  # First event has no delay
        elapsed_time = current_time - self._last_event_time
        self._last_event_time = current_time
        return elapsed_time

    def _calculate_midi_time(self, elapsed_time):
        """
        Converts elapsed time in seconds to MIDI ticks using mido.second2tick.

        Args:
            elapsed_time (float): The elapsed time in seconds.

        Returns:
            int: The elapsed time in MIDI ticks.
        """
        return int(second2tick(elapsed_time, self._ticks_per_beat, self._tempo))
