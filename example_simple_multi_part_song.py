import random
from stranger_song import StrangerBPMSong
from stranger_part import StrangerPart
from stranger_note_generator_bar_based import StrangerNoteGeneratorBarBased
from audio_engine import TonicSimpleADSRFilterSynth


scale_list = [
    [60, 62, 64, 65, 67, 69, 71],  # C Major
    [61, 63, 65, 66, 68, 70, 72],  # C# Major
    [62, 64, 66, 67, 69, 71, 73],  # D Major
    [63, 65, 67, 68, 70, 72, 74],  # D# Major
    [64, 66, 68, 69, 71, 73, 75],  # E Major
    [65, 67, 69, 70, 72, 74, 76]]  # F Major

def pick_random_note_on_scale(scale):
    return scale[random.randint(0, len(scale) - 1)]
def pick_random_scale(scale_list):
    return scale_list[random.randint(0, len(scale_list) - 1)]

class NoteGeneratorPatternScaleBased(StrangerNoteGeneratorBarBased):
    def __init__(self, control_params, synth_name, note_pattern, scale, beats_per_bar, note_value, subdivision):
        super().__init__(control_params, beats_per_bar, note_value, subdivision)
        self._synth_name = synth_name
        self._scale = scale
        self._note_pattern = note_pattern

    def _get_next_notes(self):
        on_beat, beat_counter, bar_counter, repetition_counter, max_beat, max_bar = self.get_current_beat()
        if on_beat:
            pitch, amplitude = self._note_pattern[bar_counter - 1][beat_counter - 1]
            if pitch == "random":
                pitch = pick_random_note_on_scale(self._scale)

            return [
                {
                    "synth_name": self._synth_name,
                    "event": "note_start", 
                    "pitch": pitch, 
                    "amplitude": amplitude,
                    "note_length": self._subdivision,},
            ]

        else:
            return []

    def get_part_end(self):
        part_can_end = super().get_part_can_end()

        if part_can_end:
            on_beat, beat_counter, bar_counter, repetition_counter, max_beat, max_bar = self.get_current_beat()
            if repetition_counter > 0: # play at least twice
                # Trigger part end and allow next part to play instead of this
                return True
        return False


class SimplePart(StrangerPart):
    def __init__(self, control_params, synth_name, part_name, subdivision):
        super().__init__(control_params)
        self._synth_name = synth_name
        self._part_name = part_name

        self._scale = pick_random_scale(scale_list)
        # Generate a random note pattern for the part
        note_pattern = [ # play the same random melody on the first bars on each repetition
            [
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
            ],
            [
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
                (pick_random_scale(self._scale), random.uniform(0.3, 0.7),),
                ("random", 0.7,),
                ("random", 1,),
            ]
        ]
        beats_per_bar = []
        for bar in note_pattern:
            beats_per_bar.append(len(bar))
        note_value = 4

        self._note_generator = NoteGeneratorPatternScaleBased(control_params, synth_name, note_pattern, self._scale, beats_per_bar, note_value, subdivision)

    def get_note_generator(self):
        return self._note_generator
    
    def get_part_name(self):
        return self._part_name


class SimpleMultiPartSong(StrangerBPMSong):
    def __init__(self, control_params, bpm, max_division = 16):
        super().__init__(control_params, bpm, max_division)
        self._synth_name = "simple_synth"
        self._synthesizers = {
            self._synth_name: TonicSimpleADSRFilterSynth("SquareWave", 0.05, 0.1, 0.6, 0.4, 250.0, 1.0)
        }
        self._max_division = max_division

        self._current_part_index = 0

    def get_synthesizers(self):
        return self._synthesizers
    
    def _get_next_part(self):
        """
        Generates the next part of the song.

        Returns:
            SimplePart: The next part of the song.
        """
        print(f"Starting new part: {self._current_part_index}")
        return SimplePart(
            self._control_params,
            self._synth_name,
            f"SimplePart{self._current_part_index}",
            self._max_division,
        )