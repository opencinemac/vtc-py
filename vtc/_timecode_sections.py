from typing import NamedTuple


class TimecodeSections(NamedTuple):
    """
    TimecodeSections contains the sections of a parsed timecode value as ints.
    """

    # True if this is a negative timecode. All other values will always be positive.
    negative: bool
    hours: int
    minutes: int
    seconds: int
    frames: int
