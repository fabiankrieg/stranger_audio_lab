class StrangerNoteGenerator:
    """
    Base class for generating notes for synthesizers in a structured format.

    This class provides an interface for generating a sequence of notes and operations
    for synthesizers. Subclasses should implement the `get_next_notes` method to define
    the specific behavior of the note generation.

    Interface:
        - get_next_notes(): Returns a list of dictionaries, where each dictionary
          represents a set of operations to be performed on synthesizers.

    Note Format:
        Each entry in the list returned by `get_next_notes` is a dictionary with the
        following structure:
        {
            "synth_name": {
                "event": "note_start" or "note_end",
                "pitch": <MIDI pitch> (required for "note_start"),
                "amplitude": <amplitude> (required for "note_start")
            }
        }

    Example:
        [
            {
                "square_synth": {
                    "event": "note_start",
                    "pitch": 64,
                    "amplitude": 0.5
                },
                "saw_synth": {
                    "event": "note_end"
                }
            },
            {
                "square_synth": {
                    "event": "note_end"
                }
            }
        ]

    Subclassing:
        Subclasses should override the `get_next_notes` method to implement custom
        note generation logic.
    """

    def get_next_notes(self):
        """
        Generate the next set of notes and operations for synthesizers.

        Returns:
            list: A list of dictionaries, where each dictionary represents a set of
                  operations to be performed on synthesizers.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_next_notes` method.")
