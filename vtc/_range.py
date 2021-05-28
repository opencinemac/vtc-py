from typing import Union, Optional, Container

from ._timecode import Timecode, TimecodeSource, TimecodeSourceTypes


class Range(Container[Union[TimecodeSource, "Range"]]):
    def __init__(self, tc1: Timecode, tc2: Timecode) -> None:
        """
        Represents the range between two timecodes. A timecode Range is exclusive.
        Timecode ranges cannot be negative in length, the absolute value between the two
        timecodes is used.

        :param tc1: The in point of the range.

        :param tc2: The out point of the range. This timecode is not actually in the
            range itself, but marks the delimiter where the range ends.

        :raises ValueError: when the framerates of the two timecodes do not match.

        .. note::

            If tc1 is less than tc2, the values will be flipped, and tc2 will be used
            as the in point, while tc1 is used as the out point.
        """

        if tc1.rate != tc2.rate:
            raise ValueError("Range in and out must have matching framerate")

        self._in: Timecode
        self._out: Timecode

        if tc1 < tc2:
            self._in = tc1
            self._out = tc2
        else:
            self._in = tc2
            self._out = tc1

    def __str__(self) -> str:
        return f"{self._in.timecode} - {self._out.timecode}"

    def __repr__(self) -> str:
        return f"[{self._in.timecode} - {self._out.timecode} @ {repr(self._in.rate)}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range):
            return NotImplemented

        return self._in == other._in and self._out == other._out

    def __len__(self) -> int:
        return abs(self._out - self._in).frames

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Range):
            # The range is not overlapping if this range ends before the other begins or
            # beings after the other ends
            return not (self._in >= item._out or self._out <= item._in)

        if not isinstance(item, TimecodeSourceTypes):
            return False

        return self._in <= item < self._out

    @property
    def tc_in(self) -> Timecode:
        """The in point of the range."""
        return self._in

    @property
    def tc_out(self) -> Timecode:
        """The out point of the range."""
        return self._out

    def intersection(self, other: "Range") -> Optional["Range"]:
        """
        Returns None if the two ranges do not intersect, otherwise returns the Range
        of the intersection of the two Ranges.
        """
        if other not in self:
            return None

        overlap_in = max(self._in, other._in)
        overlap_out = min(self._out, other._out)

        return Range(overlap_in, overlap_out)

    def separation(self, other: "Range") -> Optional["Range"]:
        """
        Returns None if the two ranges intersect, otherwise returns the timecode range
        between the two ranges.
        """
        if other in self:
            return None

        overlap_in = max(self._in, other._in)
        overlap_out = min(self._out, other._out)

        return Range(overlap_in, overlap_out)
