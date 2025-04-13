class StrangerPart:
    """
    Base class for managing parts of a musical composition.

    This class provides an interface for handling transitions between parts of a composition,
    retrieving the name of the current part, and obtaining the associated note generator.

    Attributes:
        control_params (audio_engine.ControlParameters): An instance of ControlParameters
            for managing and updating synthesizer parameters.

    Interface:
        - get_next_part(): Determines the next part to transition to.
        - get_part_name(): Returns the name of the current part.
        - get_note_generator(): Returns the note generator associated with the current part.

    Subclassing:
        Subclasses should override the methods to implement custom behavior for part transitions,
        naming, and note generation.

    Methods:
        - get_next_part():
            Determines the next part to transition to.

            Returns:
                str or None: The name of the next part as a string, "end" to mark the end of the song,
                             or None to replay the current part.

            Raises:
                NotImplementedError: If the method is not implemented in a subclass.

        - get_part_name():
            Retrieves the name of the current part.

            Returns:
                str: The name of the current part.

            Raises:
                NotImplementedError: If the method is not implemented in a subclass.

        - get_note_generator():
            Retrieves the note generator associated with the current part.

            Returns:
                StrangerNoteGenerator: An instance of a note generator for the current part.

            Raises:
                NotImplementedError: If the method is not implemented in a subclass.
    """

    def __init__(self, control_params):
        """
        Initializes the StrangerPart with an instance of ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
        """
        self.control_params = control_params

    def get_next_part(self):
        """
        Determines the next part to transition to.

        Returns:
            str or None: The name of the next part as a string, "end" to mark the end of the song,
                         or None to replay the current part.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_next_part` method.")

    def get_part_name(self):
        """
        Retrieves the name of the current part.

        Returns:
            str: The name of the current part.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_part_name` method.")

    def get_note_generator(self):
        """
        Retrieves the note generator associated with the current part.

        Returns:
            StrangerNoteGenerator: An instance of a note generator for the current part.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_note_generator` method.")
