import random
from stranger_song import StrangerBPMSong
from stranger_part import StrangerPart
from stranger_note_generator import StrangerNoteGenerator
from audio_engine import TonicSimpleADSRFilterSynth


class RandomNoteGenerator(StrangerNoteGenerator):
    """
    A note generator that always returns a note stop and note start for a new random note.
    """

    def __init__(self, control_params, synth_name):
        """
        Initializes the RandomNoteGenerator.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            synth_name (str): The name of the synthesizer to generate notes for.
        """
        super().__init__(control_params)
        self._synth_name = synth_name
        self._last_note = None

    def get_next_notes(self):
        """
        Generate the next set of notes for the synthesizer.

        Returns:
            list: A list of dictionaries containing note stop and note start events.
        """
        pitch = random.randint(60, 72)  # Random pitch between C4 and C5
        amplitude = 0.5  # Fixed amplitude

        return [
            {
                "synth_name": self._synth_name,
                "event": "note_start", 
                "pitch": pitch, 
                "amplitude": amplitude,
                "note_length": 4,},
        ]

    def get_part_end(self):
        """
        Always return False as this generator does not trigger part transitions.

        Returns:
            bool: False, indicating the current part does not end.
        """
        return False


class RandomNotePart(StrangerPart):
    """
    A single part that uses the RandomNoteGenerator to generate notes.
    """

    def __init__(self, control_params, synth_name):
        """
        Initializes the RandomNotePart.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            synth_name (str): The name of the synthesizer to generate notes for.
        """
        super().__init__(control_params)
        self.synth_name = synth_name
        self.note_generator = RandomNoteGenerator(control_params, synth_name)


    def get_part_name(self):
        """
        Returns the name of the current part.

        Returns:
            str: The name of the part.
        """
        return "RandomNotePart"

    def get_note_generator(self):
        """
        Returns the note generator for this part.

        Returns:
            RandomNoteGenerator: The note generator instance.
        """
        return self.note_generator


class RandomNoteSong(StrangerBPMSong):
    """
    A song that creates a single square wave synthesizer and uses a RandomNotePart.
    """

    def __init__(self, control_params, bpm):
        """
        Initializes the RandomNoteSong.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            bpm (float): Beats per minute for the song.
        """
        super().__init__(control_params, bpm, max_division=16)
        self.synth_name = "square_synth"
        self.synthesizers = {
            self.synth_name: TonicSimpleADSRFilterSynth("SquareWave", 0.05, 0.1, 0.6, 0.4, 250.0, 1.0)
        }
        self.first_part = RandomNotePart(control_params, self.synth_name)

    def get_synthesizers(self):
        """
        Returns the synthesizers in the song.

        Returns:
            dict: A dictionary of synthesizer names and their corresponding SynthWrapper instances.
        """
        return self.synthesizers
    
    def _get_next_part(self):
        """
        Always return None to replay the same part.

        Returns:
            None: Indicates the current part should be replayed.
        """
        return self.first_part
