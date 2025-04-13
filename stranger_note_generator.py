class StrangerNoteGenerator:
    """
    Base class for generating notes for synthesizers in a structured format.

    This class provides an interface for generating a sequence of notes and operations
    for synthesizers. Subclasses should implement the `get_next_notes` method to define
    the specific behavior of the note generation.

    Attributes:
        _control_params (audio_engine.ControlParameters): An instance of ControlParameters
            for managing and updating synthesizer parameters.

    Interface:
        - get_next_notes(): Returns a list of dictionaries, where each dictionary
          represents a set of operations to be performed on synthesizers.
        - get_part_end(): Returns a boolean indicating whether the current part has ended
          and a transition to the next part should be triggered.

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

    def __init__(self, control_params):
        """
        Initializes the StrangerNoteGenerator with an instance of ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
        """
        self._control_params = control_params

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

    def get_part_end(self):
        """
        Determine whether the current part of the music has ended and a transition
        to the next part should be triggered.

        Returns:
            bool: True if the current part has ended and the next part should/could be played,
                  False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_part_end` method.")
