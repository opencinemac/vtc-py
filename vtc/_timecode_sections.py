from typing import NamedTuple


class TimecodeSections(NamedTuple):
    """
    TimecodeSections contains the sections of a parsed timecode value as ints.
    """

    hours: int
    minutes: int
    seconds: int
    frames: int
