import decimal
import fractions
from typing import Union, Tuple, Optional

from ._framerate import Framerate, FramerateSource
from ._premiere_ticks import PremiereTicks
from ._consts import (
    _PPRO_TICKS_PER_SECOND,
    _FRAMES_PER_FOOT,
    _SECONDS_PER_MINUTE,
    _SECONDS_PER_HOUR,
)
from ._timecode_sections import TimecodeSections
from ._timecode_parsers import _TimecodeParseSource, _parse, _rational_to_frames
from ._timecode_dropframe import _frame_num_to_drop_frame_num


TimecodeSource = Union[_TimecodeParseSource, "Timecode"]
"""
TimecodeSource is the types of source values a timecode can be created from. See
documentation for details on how different value types as converted.
"""


class Timecode:
    def __init__(
        self,
        src: TimecodeSource,
        *,
        rate: Optional[FramerateSource],
    ) -> None:
        """
        Timecode represents the frame at a particular time in a video.

        :param src: The source value to parse. The values type determines how it is
            interpreted:

            - ``vtc.Timecode``: used the ``vtc.Timecode.rational`` seconds value to
              construct a new timecode.

            - ``string``: etiher a timecode, runtime, or feet+frames string. Runtime
              strings must have a fractal seconds place, i.e. '01:00:00.0'.

            - ``int``: frame count.

            - ``decimal.Decimal``: seconds.

            - ``float``: seconds.

            - ``fractions.Fraction``: seconds.

            - ``vtc.PremiereTicks``: Adobe Premiere Pro ticks value.

        :param rate: The framerate to use for this timecode. May be any value which
            can be passed to the constructor of :class:`Framerate` or a
            :class:`Framerate`. May only be ``None`` if ``src`` is  a :class:`Framerate`
            instance.

        :returns: A newly constructed :class:`Timecode` value.

        :raises ValueError: If a string value passed to the constructor is not a valid
            timecode, runtime, or feet+frames, or no rate value can be found.

        :raises TypeError: If passed an unsupported type.
        """
        if isinstance(src, Timecode):
            if rate is not None:
                raise ValueError(
                    "rate must be None if src is vtc.Timecode. To rebase Timecode, use"
                    "vtc.Timecode.rebase",
                )
            rate = src.rate
            src = src.rational

        if rate is None:
            raise ValueError(
                "rate must be set for all Timecode src types except vtc.Timecode",
            )

        self._rate: Framerate = Framerate(rate)
        self._value: fractions.Fraction = _parse(src, self._rate)

    def __repr__(self) -> str:
        """__repr__ prints a timecode as [01:00:00:00 @ [23.98 NTSC]]"""
        return f"[{self.timecode} @ {repr(self._rate)}]"

    def __str__(self) -> str:
        """stringing a Timecode returns the timecode value (ex: 01:00:00:00)"""
        return self.timecode

    def __eq__(self, other: object) -> bool:
        """
        Two timecodes are equal if their rational times are equal. This means that
        even if their framerates are different, two timecodes that represent
        1 hour of time exactly will be equal.

        Note that this is NOT related to actual timecode presentation. An 23.98 NTSC
        timecode of 01:00:00 will NOT be equal to a non-NTSC 23.98 timecode of
        01:00:00 because the NTSC timecode represents a rational time of slightly
        less than 1 hour.
        """
        if not isinstance(
            other, (Timecode, str, int, float, fractions.Fraction, decimal.Decimal)
        ):
            return NotImplemented

        other_tc = _coerce_other(other, self._rate)
        return self._value == other_tc._value

    def __lt__(self, other: TimecodeSource) -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value < other_tc._value

    def __le__(self, other: TimecodeSource) -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value <= other_tc._value

    def __gt__(self, other: TimecodeSource) -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value > other_tc._value

    def __ge__(self, other: TimecodeSource) -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value >= other_tc._value

    def __add__(self, other: TimecodeSource) -> "Timecode":
        other_tc = _coerce_other(other, self._rate)
        frac_value = self._value + other_tc._value
        return Timecode(frac_value, rate=self._rate)

    def __sub__(self, other: TimecodeSource) -> "Timecode":
        other_tc = _coerce_other(other, self._rate)
        frac_value = self._value - other_tc._value
        return Timecode(frac_value, rate=self._rate)

    def __mul__(
        self,
        other: Union[int, float, fractions.Fraction, decimal.Decimal],
    ) -> "Timecode":
        # Return a new timecode with the multiplication applied.
        return Timecode(round(self.frames * other), rate=self._rate)

    def __truediv__(
        self,
        other: Union[int, float, fractions.Fraction, decimal.Decimal],
    ) -> "Timecode":
        # Return a new timecode with the multiplication applied.
        return Timecode(round(self.frames / other), rate=self._rate)

    def __floordiv__(
        self,
        other: Union[int, float, fractions.Fraction, decimal.Decimal],
    ) -> "Timecode":
        # Return a new timecode with the multiplication applied.
        return Timecode(int(self.frames // other), rate=self._rate)

    def __mod__(
        self,
        other: Union[int, float, fractions.Fraction, decimal.Decimal],
    ) -> "Timecode":
        return Timecode(int(self.frames % other), rate=self._rate)

    def __divmod__(
        self,
        other: Union[int, float, fractions.Fraction, decimal.Decimal],
    ) -> Tuple["Timecode", "Timecode"]:
        dividend, modulo = divmod(self.frames, other)
        return (
            Timecode(int(dividend), rate=self._rate),
            Timecode(int(modulo), rate=self._rate),
        )

    def __neg__(self) -> "Timecode":
        return Timecode(-self._value, rate=self._rate)

    def __abs__(self) -> "Timecode":
        return Timecode(abs(self._value), rate=self._rate)

    @property
    def rate(self) -> Framerate:
        """rate is the framerate at which this timecode is being interpreted"""
        return self._rate

    @property
    def rational(self) -> fractions.Fraction:
        """
        frac is a rational (fraction) representation of number of seconds this timecode
        represents.
        """
        return self._value

    @property
    def sections(self) -> TimecodeSections:
        """
        sections returns the sections of a timecode as ints for callers to
        format/work on as desired.
        """
        rate = self._rate
        frames_number = abs(self.frames)

        if self._rate.dropframe:
            # We need to do an adjustment for drop-frame timecode
            frames_number = _frame_num_to_drop_frame_num(
                frames_number,
                self.rate.timebase,
            )

        timebase = rate.timebase

        hours, frames = divmod(frames_number, timebase * _SECONDS_PER_HOUR)
        minutes, frames = divmod(frames, timebase * _SECONDS_PER_MINUTE)
        seconds, frames = divmod(frames, timebase)

        return TimecodeSections(
            # If our value is less than 0, this is a negative value.
            negative=self._value < 0,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            frames=round(frames),
        )

    @property
    def timecode(self) -> str:
        """
        timecode returns the formatted SMPTE timecode: (ex: 01:00:00:00).
        """
        sections = self.sections

        frames_sep = ":"
        if self._rate.dropframe:
            frames_sep = ";"

        timecode = (
            f"{str(sections.hours).zfill(2)}"
            f":{str(sections.minutes).zfill(2)}"
            f":{str(sections.seconds).zfill(2)}"
            f"{frames_sep}{str(sections.frames).zfill(2)}"
        )
        return _add_neg_to_rep(self._value, timecode)

    @property
    def frames(self) -> int:
        """
        frames returns the frame number of this timecode (how many frames would have
        played starting at 0 between 00:00:00:00 and the tc this value represents.).
        """
        return _rational_to_frames(self._value, self._rate)

    @property
    def feet_and_frames(self) -> str:
        """
        returns the number of feet and frames this timecode represents if it were
        shot on 35mm 4-perf film (16 frames per foot). ex: '5400+13'.

        feet and frames is most commonly used as a reference in the sound mixing world.
        """
        feet, frames = divmod(abs(self.frames), _FRAMES_PER_FOOT)
        feet_and_frames = f"{feet}+{str(frames).zfill(2)}"
        return _add_neg_to_rep(self._value, feet_and_frames)

    @property
    def seconds(self) -> decimal.Decimal:
        """
        seconds returns the number of seconds that would have elapsed between
        00:00:00:00 and the timecode this value represents.

        This value is a decimal.Decimal value to avoid floating-point shenanigans.
        """
        return decimal.Decimal(self._value.numerator) / decimal.Decimal(
            self._value.denominator
        )

    @property
    def premiere_ticks(self) -> PremiereTicks:
        """
        premiere_ticks returns the number of elapsed ticks this timecode represents in
        Adobe Premiere Pro.

        Premiere uses ticks internally to track elapsed time. A second contains
        254016000000 ticks, regardless of framerate.

        These ticks are present in Premiere FCP7XML cutlists, and can sometimes be used
        for more precise calculations during respeeds.

        Ticks are also used for scripting in Premiere Panels.
        """
        return PremiereTicks(round(self._value * _PPRO_TICKS_PER_SECOND))

    def runtime(self, precision: Optional[int] = 9) -> str:
        """
        Runtime returns the true runtime of the timecode in HH:MM:SS.FFFFFFFFF format.

        :param precision: how many places to print for fractional seconds.
            None=no rounding.

        Runtime will always be returned with at least one decimal place in order to
        distinguish it from timecode without an hours value. A runtime of exactly one
        hour will be returned as '01:00:00.0'

        Note: The true runtime will often diverge from the hours, minutes, and seconds
            value of the timecode representation when dealing with non-whole-frame
            framerates. Even drop-frame timecode does not continuously adhere 1:1 to the
            actual runtime. For instance, [01:00:00;00 @ 29.97 DF] has a true runtime of
            '00:59:59.9964', and [01:00:00:00 @ 23.98 NTSC] has a true runtime of
            '01:00:03.6'
        """
        seconds = round(abs(self.seconds), ndigits=precision)

        hours, seconds = divmod(seconds, _SECONDS_PER_HOUR)
        minutes, seconds = divmod(seconds, _SECONDS_PER_MINUTE)
        seconds, fractal = divmod(seconds, 1)
        if fractal == 0:
            fractal_str = ".0"
        else:
            fractal_str = "." + str(fractal).split(".")[-1].rstrip("0")

        runtime = (
            f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:"
            f"{str(seconds).zfill(2)}{fractal_str}"
        )

        return _add_neg_to_rep(self._value, runtime)

    def rebase(self, new_rate: FramerateSource) -> "Timecode":
        """
        rebase re-calculates the timecode at a new frame rate based on the frame-count
        value of the current timecode.

        :param new_rate: the new rate to rebase at.

        :returns: The new, rebased timecode.
        """
        return Timecode(self.frames, rate=new_rate)


def _add_neg_to_rep(frac_val: fractions.Fraction, rep: str) -> str:
    """
    _add_neg_to_rep adds a negative sign to a string tc representation if the value is
    less than 0.
    """
    if frac_val >= 0:
        return rep

    return "-" + rep


def _coerce_other(other: TimecodeSource, this_rate: Framerate) -> Timecode:
    """
    coerce other coerces a value to a timecode that an existing timecode needs to do
    an operation with. If the other value is not a timecode, the rate of the ecisting
    timecode will be used in parsing the other value.
    """
    if isinstance(other, Timecode):
        return other

    return Timecode(other, rate=this_rate)
