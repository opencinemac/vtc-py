import fractions
import decimal
import re
from typing import Union, List

from ._framerate import Framerate
from ._premiere_ticks import PremiereTicks
from ._timecode_sections import TimecodeSections
from ._timecode_dropframe import _parse_drop_frame_adjustment
from ._consts import (
    _tc_regex,
    _runtime_regex,
    _feet_and_frames_regex,
    _SECONDS_PER_MINUTE,
    _SECONDS_PER_HOUR,
    _FRAMES_PER_FOOT,
    _PPRO_TICKS_PER_SECOND,
)


# Union type detailing what types a Timecode can be parsed from.
_TimecodeParseSource = Union[
    str,
    int,
    float,
    fractions.Fraction,
    decimal.Decimal,
    PremiereTicks,
]


def _parse(src: _TimecodeParseSource, rate: Framerate) -> fractions.Fraction:
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

    # If we got a hit on the negative group, this value is negative.
    is_negative = matched.group("negative") is not None

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
        calc_rate = Framerate(round(rate.playback), ntsc=False)
    else:
        calc_rate = rate

    drop_adjustment = fractions.Fraction(0, 1)
    if rate.dropframe:
        drop_adjustment = _parse_drop_frame_adjustment(
            sections=TimecodeSections(
                negative=is_negative,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                frames=frames,
            ),
            rate=calc_rate,
        )

    # Divide the frames by the rate then add to the seconds value.
    seconds = seconds + minutes * _SECONDS_PER_MINUTE + hours * _SECONDS_PER_HOUR

    # Now get the frames as a fractional and then convert to an int.
    frames_frac = frames + seconds * calc_rate.playback

    # Add the drop-frame drop_adjustment
    frames_frac += drop_adjustment

    if is_negative:
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


def _parse_int(frames: int, rate: Framerate) -> fractions.Fraction:
    """_parse_int converts the frame count into rational time."""
    return frames / rate.playback


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


def _rational_to_frames(seconds: fractions.Fraction, rate: Framerate) -> int:
    """_rational_to_frames converts rational seconds to a frame count."""
    # multiply the fraction to frames.
    frac_frames = seconds * rate.playback

    # If this value converted cleanly, we can just return the numerator.
    if frac_frames.denominator == 1:
        return frac_frames.numerator

    # Otherwise lets convert to a float, then round.
    return round(float(frac_frames))
