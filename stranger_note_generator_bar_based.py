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
        self._subdivision_counter = -1
        self._beat_counter = -1
        self._bar_counter = 0
        self._repetition_counter = 0
        self._on_beat = True

    def _update_beat(self):
        """
        Updates the beat, bar, and repetition counters based on the current state.
        """
        total_beats_in_bar = self._beats_per_bar[self._bar_counter]

        self._subdivision_counter += 1

        # Update on_beat
        if self._subdivision_counter % self._note_value == 0:
            self._on_beat = True
            self._beat_counter += 1
        else:
            self._on_beat = False

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
                - int: `max_beat` indicating the last beat within the bar.
                - int: `max_bar` indicating the last bar in the sequence.
        """
        return self._on_beat, self._beat_counter + 1, self._bar_counter + 1, self._repetition_counter, self._beats_per_bar[self._bar_counter], len(self._beats_per_bar)

    def get_next_notes(self):
        """
        Generate the next set of notes and operations for synthesizers.

        Returns:
            list: A list of dictionaries, where each dictionary represents a set of
                  operations to be performed on synthesizers.
        """
        self._update_beat()  # Update the beat
        new_notes = self._get_next_notes()
        return new_notes

    def _get_next_notes(self):
        """
        Generate the next set of notes and operations for synthesizers.

        Returns:
            list: A list of dictionaries, where each dictionary represents a set of
                  operations to be performed on synthesizers.
        """
        # Placeholder for actual note generation logic
        raise NotImplementedError("Subclasses must implement the `_get_next_notes` method.")

    def get_part_end(self):
        """
        Always return False as this generator does not trigger part transitions.

        Returns:
            bool: False, indicating the current part does not end.
        """
        return False



# Unit test for StrangerNoteGeneratorBarBased
if __name__ == "__main__":
    import unittest
    class TestStrangerNoteGeneratorBarBased(unittest.TestCase):
        def test_beat_counting(self):
            """
            Test the beat counting functionality with a custom beat sequence.
            """
            class TestNoteGenerator(StrangerNoteGeneratorBarBased):
                def _get_next_notes(self):
                    pass  # No-op for testing

            # Create an instance of the test generator
            control_params = None  # Placeholder, as ControlParameters is not used in this test
            beats_per_bar = [3, 4, 1, 2]
            note_value = 4
            subdivision = 16
            generator = TestNoteGenerator(control_params, beats_per_bar, note_value, subdivision)

            # Expected results for each update
            expected_results = [
                (True, 1, 1, 0, 3, 4),  # On beat 1 of bar 1
                (True, 2, 1, 0, 3, 4),  # On beat 2 of bar 1
                (True, 3, 1, 0, 3, 4),  # On beat 3 of bar 1
                (True, 1, 2, 0, 4, 4),  # On beat 1 of bar 2
                (True, 2, 2, 0, 4, 4),  # On beat 2 of bar 2
                (True, 3, 2, 0, 4, 4),  # On beat 3 of bar 2
                (True, 4, 2, 0, 4, 4),  # On beat 4 of bar 2
                (True, 1, 3, 0, 1, 4),  # On beat 1 of bar 3
                (True, 1, 4, 0, 2, 4),  # On beat 1 of bar 4
                (True, 2, 4, 0, 2, 4),  # On beat 2 of bar 4
                (True, 1, 1, 1, 3, 4),  # Back to bar 1, repetition 1
            ]

            num_of_subdivisions_per_beat = subdivision // note_value

            for index in range(len(expected_results) * num_of_subdivisions_per_beat):
                # Call the method to update the beat
                generator.get_next_notes()
                
                test_on_beat = index % num_of_subdivisions_per_beat == 0

                # Check if the current beat information matches the expected results
                expected = expected_results[index // num_of_subdivisions_per_beat]
                # Get the current beat information
                on_beat, beat_counter, bar_counter, repetition_counter, max_beat, max_bar = generator.get_current_beat()

                self.assertEqual(on_beat, test_on_beat)
                self.assertEqual(beat_counter, expected[1])
                self.assertEqual(bar_counter, expected[2])
                self.assertEqual(repetition_counter, expected[3])
                self.assertEqual(max_beat, expected[4])
                self.assertEqual(max_bar, expected[5])


    
    # Run the tests
    unittest.main()
