class StrangerSong:
    """
    Base class for managing a song composed of synthesizers and musical parts.

    This class provides an interface for transitioning between parts, managing synthesizers,
    and determining the update interval.

    Attributes:
        _control_params (audio_engine.ControlParameters): An instance of ControlParameters
            for managing and updating synthesizer parameters.
        
    Interface:
        - get_synthesizers(): Returns a dictionary of synthesizer names and their corresponding SynthWrapper instances.
        - get_update_interval(): Returns the minimum note duration (update interval) in seconds.
        - get_next_part(current_part_name): Returns the name of the next part based on the current part.
    """

    def __init__(self, control_params):
        """
        Initializes the StrangerSong with an instance of ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
        """
        self._control_params = control_params
        self._current_part_index = 0

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

    def get_next_part(self):
        """
        Determines the next part of the song by incrementing the part counter and calling the subclass implementation.

        Returns:
            StrangerPart or None: The next part of the song, or "end" to mark the end of the song,
            or None to repeat the current part.
        """
        self._current_part_index += 1
        return self._get_next_part()
    
    def get_current_part_index(self):
        """
        Returns the current part index.

        Returns:
            int: The current part index.
        """
        return self._current_part_index

    def _get_next_part(self):
        """
        Private virtual function to be implemented by subclasses to determine the next part.

        Returns:
            StrangerPart or None: The next part of the song, or "end" to mark the end of the song,
            or None to repeat the current part.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `_get_next_part` method.")


class StrangerBPMSong(StrangerSong):
    """
    Subclass of StrangerSong that calculates the update interval based on BPM and max division.

    Attributes:
        _bpm (float): Beats per minute for the song.
        _max_division (int): Maximum division for note duration (e.g., 16 for 16th notes).
    """

    def __init__(self, control_params, bpm, max_division):
        """
        Initializes the StrangerBPMSong with BPM, max division, and ControlParameters.

        Args:
            control_params (audio_engine.ControlParameters): An instance of ControlParameters.
            bpm (float): Beats per minute for the song.
            max_division (int): Maximum division for note duration (e.g., 16 for 16th notes).
        """
        super().__init__(control_params)
        self._bpm = bpm
        self._max_division = max_division

    def get_update_interval(self):
        """
        Calculates the minimum note duration (update interval) based on BPM and max division.

        Returns:
            float: The minimum note duration in seconds.
        """
        return 60 / self._bpm / (self._max_division / 4)
