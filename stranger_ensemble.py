class StrangerEnsemble:
    """
    Base class for managing an ensemble of synthesizers and musical parts.

    This class provides an interface for retrieving the first part of the composition,
    accessing the synthesizers in the ensemble, and determining the update interval
    for the note generation loop.

    Attributes:
        control_params (audio_engine.ControlParameters): An instance of ControlParameters
            for managing and updating synthesizer parameters.

    Interface:
        - get_first_part(): Returns the first part of the composition as a StrangerPart instance.
        - get_synthesizers(): Returns a dictionary of synthesizer names and their corresponding SynthWrapper instances.
        - get_update_interval(): Returns the minimum note duration (update interval) in seconds.
    """

    def __init__(self, control_params):
        """
        Initializes the StrangerEnsemble with an instance of ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
        """
        self.control_params = control_params

    def get_first_part(self):
        """
        Returns the first part of the composition.

        Returns:
            StrangerPart: An instance of the first part of the composition.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_first_part` method.")

    def get_synthesizers(self):
        """
        Returns a dictionary of synthesizer names and their corresponding SynthWrapper instances.

        Returns:
            dict: A dictionary where keys are synthesizer names (str) and values are SynthWrapper instances.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_synthesizers` method.")

    def get_update_interval(self):
        """
        Returns the minimum note duration (update interval) in seconds.

        Returns:
            float: The minimum note duration in seconds.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `get_update_interval` method.")


class StrangerBPMEnsemble(StrangerEnsemble):
    """
    Subclass of StrangerEnsemble that calculates the update interval based on BPM and max division.

    Attributes:
        bpm (float): Beats per minute for the composition.
        max_division (int): Maximum division for note duration (e.g., 16 for 16th notes).
    """

    def __init__(self, control_params, bpm, max_division):
        """
        Initializes the StrangerBPMEnsemble with BPM, max division, and ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            bpm (float): Beats per minute for the composition.
            max_division (int): Maximum division for note duration (e.g., 16 for 16th notes).
        """
        super().__init__(control_params)
        self.bpm = bpm
        self.max_division = max_division

    def get_update_interval(self):
        """
        Calculates the minimum note duration (update interval) based on BPM and max division.

        Returns:
            float: The minimum note duration in seconds.
        """
        return 60 / self.bpm / (self.max_division / 4)
