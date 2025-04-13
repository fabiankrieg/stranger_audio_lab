from stranger_note_generator import StrangerNoteGenerator


class StrangerNoteGeneratorBarBased(StrangerNoteGenerator):
    """
    A note generator that tracks the current beat, bar, and repetition based on the time signature
    and subdivision of the part.

    Attributes:
        _beats_per_bar (list of int): A list specifying the number of beats per bar for each bar in the sequence.
        _note_value (int): The note value for the time signature (e.g., 4 for quarter notes, 8 for eighth notes).
        _subdivision (int): The current subdivision (e.g., 16 for 16th notes).
        _beat_counter (int): Tracks the total number of beats processed.
        _bar_counter (int): Tracks the current bar in the sequence.
        _repetition_counter (int): Tracks the number of times the sequence of bars has been repeated.
        _on_beat (bool): Indicates if the current subdivision is on a beat.
    """

    def __init__(self, control_params, beats_per_bar, note_value, subdivision):
        """
        Initializes the StrangerNoteGeneratorBarBased.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            beats_per_bar (list of int): A list specifying the number of beats per bar for each bar in the sequence.
            note_value (int): The note value for the time signature (e.g., 4 for quarter notes, 8 for eighth notes).
            subdivision (int): The current subdivision (e.g., 16 for 16th notes).
        """
        super().__init__(control_params)
        self._beats_per_bar = beats_per_bar
        self._note_value = note_value
        self._subdivision = subdivision
        self._beat_counter = 0
        self._bar_counter = 0
        self._repetition_counter = 0
        self._on_beat = False

    def _update_beat(self):
        """
        Updates the beat, bar, and repetition counters based on the current state.
        """
        total_beats_in_bar = self._beats_per_bar[self._bar_counter]
        self._beat_counter += 1

        # Update on_beat
        self._on_beat = (self._beat_counter % (self._subdivision // self._note_value)) == 0

        # Move to the next bar if the current bar is complete
        if self._beat_counter >= total_beats_in_bar:
            self._beat_counter = 0
            self._bar_counter += 1

            # If all bars are completed, reset to the first bar and increment repetition
            if self._bar_counter >= len(self._beats_per_bar):
                self._bar_counter = 0
                self._repetition_counter += 1

    def get_current_beat(self):
        """
        Returns the current beat, bar, and repetition assuming the update has already been performed.

        Returns:
            tuple: A tuple containing:
                - bool: `on_beat` indicating if the current subdivision is on a beat.
                - int: `beat` indicating the current beat within the bar.
                - int: `bar` indicating the current bar in the sequence.
                - int: `repetition` indicating the current repetition of the bar sequence.
        """
        return self._on_beat, self._beat_counter + 1, self._bar_counter + 1, self._repetition_counter

    def get_next_notes(self):
        """
        Generate the next set of notes and operations for synthesizers.

        Returns:
            list: A list of dictionaries, where each dictionary represents a set of
                  operations to be performed on synthesizers.
        """
        self._update_beat()  # Update the beat before generating notes
        # Example implementation: Always return an empty list for now
        return []

    def get_part_end(self):
        """
        Always return False as this generator does not trigger part transitions.

        Returns:
            bool: False, indicating the current part does not end.
        """
        return False
