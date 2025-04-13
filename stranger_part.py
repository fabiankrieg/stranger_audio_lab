class StrangerPart:
    """
    Base class for managing parts of a musical composition.

    This class provides an interface for retrieving the name of the current part
    and obtaining the associated note generator.

    Attributes:
        _control_params (audio_engine.ControlParameters): An instance of ControlParameters
            for managing and updating synthesizer parameters.

    Interface:
        - get_part_name(): Returns the name of the current part.
        - get_note_generator(): Returns the note generator associated with the current part.
    """

    def __init__(self, control_params):
        """
        Initializes the StrangerPart with an instance of ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
        """
        self._control_params = control_params

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
