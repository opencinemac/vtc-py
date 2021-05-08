import decimal
import fractions
import re
from typing import Union, List, Tuple, Optional

from ._framerate import Framerate, FramerateSource
from ._premiere_ticks import PremiereTicks
from ._consts import (
    _runtime_regex,
    _tc_regex,
    _feet_and_frames_regex,
    _PPRO_TICKS_PER_SECOND,
    _FRAMES_PER_FOOT,
    _SECONDS_PER_MINUTE,
    _SECONDS_PER_HOUR,
)


class Timecode:
    def __init__(
        self,
        src: "TimecodeSource",
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
        if isinstance(src, Timecode) and rate is not None:
            raise ValueError(
                "rate must be None if src is vtc.Timecode. To rebase Timecode, use"
                "vtc.Timecode.rebase",
            )

        parse_rate = rate
        if parse_rate is None:
            if not isinstance(src, Timecode):
                raise ValueError(
                    "rate must be set for all Timecode src types except vtc.Timecode",
                )
            parse_rate = src.rate

        self._rate: Framerate = Framerate(parse_rate)
        self._value: fractions.Fraction = _parse(src, self._rate)

    def __repr__(self) -> str:
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

    def __lt__(self, other: "TimecodeSource") -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value < other_tc._value

    def __le__(self, other: "TimecodeSource") -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value <= other_tc._value

    def __gt__(self, other: "TimecodeSource") -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value > other_tc._value

    def __ge__(self, other: "TimecodeSource") -> bool:
        other_tc = _coerce_other(other, self._rate)
        return self._value >= other_tc._value

    def __add__(self, other: "TimecodeSource") -> "Timecode":
        other_tc = _coerce_other(other, self._rate)
        frac_value = self._value + other_tc._value
        return Timecode(frac_value, rate=self._rate)

    def __sub__(self, other: "TimecodeSource") -> "Timecode":
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
    def timecode(self) -> str:
        """
        timecode returns the formatted SMPTE timecode: (ex: 01:00:00:00).
        """
        rate = self._rate
        frames_number = abs(self.frames)

        if self._rate.drop_frame:
            # We need to do an adjustment for drop-frame timecode
            frames_number = _frame_num_to_drop_frame_num(frames_number, self._rate)

        if rate.ntsc:
            # If this is an ntsc frame rate, we need to present the timecode as if it
            # were a whole-frame framerate (23.98 gets presented as if it were 24).
            rate = Framerate(round(self._rate.frac))

        rate_int = int(rate.frac)
        hours, frames = divmod(frames_number, rate_int * _SECONDS_PER_HOUR)
        minutes, frames = divmod(frames, rate_int * _SECONDS_PER_MINUTE)
        seconds, frames = divmod(frames, rate_int)

        frames_sep = ":"
        if self._rate.drop_frame:
            frames_sep = ";"

        timecode = (
            f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}"
            f":{str(seconds).zfill(2)}{frames_sep}{str(frames).zfill(2)}"
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
        """
        return Timecode(self.frames, rate=new_rate)


TimecodeSource = Union[
    Timecode,
    str,
    int,
    float,
    fractions.Fraction,
    decimal.Decimal,
    PremiereTicks,
]
"""
TimecodeSource is the types of source values a timecode can be created from. See
documentation for details on how different value types as converted.
"""


def _add_neg_to_rep(frac_val: fractions.Fraction, rep: str) -> str:
    """
    _add_neg_to_rep adds a negative sign to a string tc representation if the value is
    less than 0.
    """
    if frac_val >= 0:
        return rep

    return "-" + rep


def _frame_num_to_drop_frame_num(frame_number: int, rate: Framerate) -> int:
    """
    _frame_num_to_drop_frame_num converts a frame-number to an adjusted frame number for
    creating drop-frame tc.
    """
    # Get the whole-frame rate (ex: 29.97 -> 30)
    rate_whole = round(rate.frac)

    # Get the number frames-per-minute at the whole-frame rate
    frames_per_minute_whole = rate_whole * 60
    # Get the number of frames we need to drop each time we drop frames (ex: 2 or 29.97)
    drop_frames = round(rate_whole * 0.066666)

    # Get the number of frames are in a minute where we have dropped frames at the
    # beginning
    frames_per_minute_drop = (rate_whole * 60) - drop_frames
    # Get the number of actual frames in a 10-minute span for drop frame timecode. Since
    # we drop 9 times a minute, it will be 9 drop-minute frame counts + 1 whole-minute
    # frame count.
    frames_per_10minutes_drop = frames_per_minute_drop * 9 + frames_per_minute_whole

    # Get the number of 10s of minutes in this count, and the remaining frames.
    tens_of_minutes, frames = divmod(frame_number, frames_per_10minutes_drop)

    # Create an adjustment for the number of 10s of minutes. It will be 9 times the
    # drop value (we drop for the first 9 minutes, then leave the 10th alont.).
    adjustment = 9 * drop_frames * tens_of_minutes

    # Of our remaining frames are less than a whole minute, we aren't going to drop
    # again. Add the adjustment and return
    if frames < frames_per_minute_whole:
        return frame_number + adjustment

    # Remove the first full minute (we don't drop until the next minute) and add the
    # drop-rate to the adjustment.
    frames -= rate_whole
    adjustment += drop_frames

    # Get the number of remaining drop-minutes present, and add a drop adjustment for
    # each
    minutes_drop = frames // frames_per_minute_drop
    adjustment += minutes_drop * drop_frames

    # Return our original frame number adjusted by our calculated adjustment.
    return frame_number + adjustment


def _rational_to_frames(seconds: fractions.Fraction, rate: Framerate) -> int:
    """_rational_to_frames converts rational seconds to a frame count."""
    # multiply the fraction to frames.
    frac_frames = seconds * rate.frac

    # If this value converted cleanly, we can just return the numerator.
    if frac_frames.denominator == 1:
        return frac_frames.numerator

    # Otherwise lets convert to a float, then round.
    return round(float(frac_frames))


def _parse(src: TimecodeSource, rate: Framerate) -> fractions.Fraction:
    """_parse converts an input value and rate into rational time."""
    if isinstance(src, str):
        return _parse_str(src, rate)
    # Premiere ticks check needs to come before int since it inherits int.
    elif isinstance(src, PremiereTicks):
        return _parse_premiere_ticks(src, rate)
    elif isinstance(src, int):
        return _parse_int(src, rate)
    elif isinstance(src, float):
        return _parse_float(src, rate)
    elif isinstance(src, decimal.Decimal):
        return _parse_decimal(src, rate)
    elif isinstance(src, Timecode):
        return src.rational
    elif isinstance(src, fractions.Fraction):
        return _parse_fraction(src, rate)
    else:
        raise TypeError(f"unsupported type for Timecode conversion: {type(src)}")


def _parse_str(src: str, rate: Framerate) -> fractions.Fraction:
    """
    parse non-numeric string parses a string that represents a timecode, runtime or
    feet+frames.
    """
    # Match against our tc regex.
    matched = _tc_regex.fullmatch(src)
    if matched:
        return _parse_tc_str(matched, rate)

    matched = _runtime_regex.fullmatch(src)
    if matched:
        return _parse_runtime_str(matched, rate)

    matched = _feet_and_frames_regex.fullmatch(src)
    if matched:
        return _parse_feet_and_frames_str(matched, rate)

    # If there is no match, raise a regex error.
    raise ValueError(f"{repr(src)} is not a recognized timecode format")


def _parse_tc_str(matched: re.Match, rate: Framerate) -> fractions.Fraction:
    """
    _parse_tc_str converts a timecode string (ex: 01:00:00:00) into a fractional
    seconds value.
    """
    # We will always have a 'frames' group.
    frames: int = int(matched.group("frames"))
    # Some timecodes may be abbreviated, so the other three sections may or may not be
    # present. Gather them then filter out empty sections.
    groups: List[int] = [
        matched.group("section1"),
        matched.group("section2"),
        matched.group("section3"),
    ]
    groups = [x for x in groups if x]

    # Work backwards to fill in the sections that are present, otherwise the value is
    # '0'.
    seconds = 0
    minutes = 0
    hours = 0
    if len(groups) >= 1:
        seconds = int(groups[-1])
    if len(groups) >= 2:
        minutes = int(groups[-2])
    if len(groups) >= 3:
        hours = int(groups[-3])

    if rate.ntsc:
        calc_rate = Framerate(round(rate.frac), ntsc=False)
    else:
        calc_rate = rate

    if rate.drop_frame:
        frames_frac = _parse_drop_frame(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            frames=frames,
            rate=calc_rate,
        )
    else:
        # Divide the frames by the rate then add to the seconds value.
        seconds = seconds + minutes * _SECONDS_PER_MINUTE + hours * _SECONDS_PER_HOUR

        # Now get the frames as a fractional and then convert to an int.
        frames_frac = frames + seconds * calc_rate.frac

    if matched.group("negative"):
        frames_frac = -frames_frac

    # Now parse the frame count.
    return _parse_int(round(frames_frac), rate)


def _parse_runtime_str(matched: re.Match, rate: Framerate) -> fractions.Fraction:
    """
    _parse_runtime_str parses a runtime string (ex 01:00:00.6) into a fractional
    seconds value.
    """
    # We will always have a 'frames' group.
    seconds: decimal.Decimal = decimal.Decimal(matched.group("seconds"))
    # Some timecodes may be abbreviated, so the other three sections may or may not be
    # present. Gather them then filter out empty sections.
    groups: List[int] = [
        matched.group("section1"),
        matched.group("section2"),
    ]

    groups = [x for x in groups if x]

    # Work backwards to fill in the sections that are present, otherwise the value is
    # '0'.
    minutes = 0
    hours = 0
    if len(groups) >= 1:
        minutes = int(groups[-1])
    if len(groups) >= 2:
        hours = int(groups[-2])

    # Calculate the number of seconds as a decimal, then use our decimal parser to
    # arrive at the correct result.
    seconds = seconds + minutes * _SECONDS_PER_MINUTE + hours * _SECONDS_PER_HOUR

    if matched.group("negative"):
        seconds = -seconds

    return _parse_decimal(seconds, rate)


def _parse_feet_and_frames_str(
    matched: re.Match,
    rate: Framerate,
) -> fractions.Fraction:
    """
    _parse_runtime_str parses a feet+frames string (ex 5400+13) into a fractional
    seconds value.
    """
    feet_str = matched.group("feet")
    frames_str = matched.group("frames")

    # Get the total frame count.
    frames = int(feet_str) * _FRAMES_PER_FOOT + int(frames_str)

    if matched.group("negative"):
        frames = -frames

    # Pass it off to our frame count parser.
    return _parse_int(frames, rate)


def _parse_drop_frame(
    hours: int,
    minutes: int,
    seconds: int,
    frames: int,
    rate: Framerate,
) -> fractions.Fraction:
    """_parse_drop_frame adjusts the frame number based on drop-frame TC conventions"""
    if (frames == 0 or frames == 1) and minutes % 10 != 0 and minutes != 0:
        raise ValueError(
            f"drop-frame tc cannot have a frames value of {frames} on minutes not "
            f"divisible by 10",
        )

    rate_whole = round(rate.frac)
    drop_frames = round(rate_whole * 0.066666)
    frames_per_hour = _SECONDS_PER_HOUR * rate_whole
    frames_per_minute = _SECONDS_PER_MINUTE * rate_whole

    total_minutes = 60 * hours + minutes
    adjustment = drop_frames * (total_minutes - total_minutes // 10)

    frame_number = (
        hours * frames_per_hour
        + minutes * frames_per_minute
        + seconds * rate_whole
        + frames
        - adjustment
    )
    return fractions.Fraction(frame_number, 1)


def _parse_int(frames: int, rate: Framerate) -> fractions.Fraction:
    """_parse_int converts the frame count into rational time."""
    return frames / rate.frac


def _parse_float(seconds: float, rate: Framerate) -> fractions.Fraction:
    """_parse_float converts the seconds value into rational time."""
    frames = _rational_to_frames(fractions.Fraction(seconds), rate)
    return _parse_int(frames, rate)


def _parse_fraction(seconds: fractions.Fraction, rate: Framerate) -> fractions.Fraction:
    """
    _parse_fraction parses a fractional seconds value to a fractional frames value.
    """
    return _parse_int(_rational_to_frames(seconds, rate), rate)


def _parse_decimal(seconds: decimal.Decimal, rate: Framerate) -> fractions.Fraction:
    """
    _parse_decimal parses a decimal.Decimal seconds value to a frame count fractional
    value.
    """
    frames = _rational_to_frames(fractions.Fraction(seconds), rate)
    return _parse_int(frames, rate)


def _parse_premiere_ticks(ticks: PremiereTicks, rate: Framerate) -> fractions.Fraction:
    seconds = ticks / _PPRO_TICKS_PER_SECOND
    return _parse_fraction(seconds, rate)


def _coerce_other(other: TimecodeSource, this_rate: Framerate) -> Timecode:
    """
    coerce other coerces a value to a timecode that an existing timecode needs to do
    an operation with. If the other value is not a timecode, the rate of the ecisting
    timecode will be used in parsing the other value.
    """
    if isinstance(other, Timecode):
        return other

    return Timecode(other, rate=this_rate)
