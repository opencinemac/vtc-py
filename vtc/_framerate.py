import dataclasses
import fractions
from typing import Union, Tuple, Optional


class Framerate:
    def __init__(
        self,
        src: "FramerateSource",
        *,
        ntsc: Optional[bool] = None,
        dropframe: bool = False,
    ) -> None:
        """
        Framerate is the rate at which a video file frames are played back.

        Framerate is measured in frames-per-second (24/1 = 24 frames-per-second).

        :param src: the source value to parse to a Framerate. src must conform to
            one of the following value types:

            - :class:`Framerate`: Another timebase value.

            - ``str``: Strings may be of a fractional value ('24/1'), whole numbers
              representing the fps ('24') OR decimal numbers like ('23.9876') or 23.98.
              Such values will be converted to their actual meaning (24000/1001).

            - ``Tuple[int, int]``: Numerator and denominator of a fraction.

            - ``fractions.Fraction`` value.

            - ``float`` value -- only allowed if ntsc=true.

            .. note ::

                if a value like 1/24 is passed in (where the numerator is less than
                the denominator), the value will be converted to 24/1 after being
                parsed.

        :param ntsc: Whether timecode should be calculated via NTSC convention.

            For NTSC, playback speed is 23.976, the TIMECODE is still calculated as if
            it were at 24fps, which affects how a :func:`~Timecode.timecode` value
            will be rendered.

            When ``None``, non-whole number floats like 23.98 and fractional values
            with a denominator of 1001 will be assumed to be ntsc, but whole-numbers
            will be left as-is.

            When this option is ``True``, the framerate will be rounded to the nearest
            whole number before the :func:`~Timecode.timecode` representation is
            calculated.

        :param dropframe: Whether this is a drop-frame style timecode (only available
            for frame rates divisible by 30000/1001 like 29.97 and 59.94).
        """
        dropframe, ntsc = _validate_dropframe_ntsc(ntsc, dropframe)

        self._value: fractions.Fraction
        self._dropframe = dropframe
        self._ntsc: bool

        # Parse tha value into a timebase.
        self._value = _parse(src, ntsc)
        if isinstance(src, Framerate):
            self._dropframe = src.dropframe
            ntsc = src.ntsc

        self._ntsc = _infer_ntsc(self._value, ntsc)
        _validate_drop_frame_value(self._value, self._dropframe)

    def __str__(self) -> str:
        """Returns the framerate as a fractional string (ex: '24/1')."""
        return str(self._value)

    def __repr__(self) -> str:
        """Returns formatted framerate information: (ex: '[24/1 fps NTSC]')."""
        rate_value = str(round(float(self._value), 2)).rstrip("0").rstrip(".")
        value = f"[{rate_value}"
        if self._ntsc:
            value += " NTSC"

        if self._dropframe:
            value += " DF"

        value += "]"

        return value

    def __eq__(self, other: object) -> bool:
        """
        Two Framerate instances are equal if their fractional value, ntsc attribute and
        drop frame attribute are equal.
        """
        if not isinstance(other, Framerate):
            return NotImplemented

        return (
            self._value == other._value
            and self._ntsc == other._ntsc
            and self._dropframe == other._dropframe
        )

    @property
    def playback(self) -> fractions.Fraction:
        """
        The rational representation of the real-world video playback speed in
        frames-per-second as a fraction.

        example: 24000/1001.

        .. note::
            :func:`~Framerate.playback` and :func:`~Framerate.timebase` only differ in
            NTSC framerates. All non-NTSC framerates will have identical values for
            both properties.
        """
        return self._value

    @property
    def timebase(self) -> fractions.Fraction:
        """
        The rational representation of the timecode display speed in frames-per-second
        as a fraction.

        example: 24/1

        .. note::
            :func:`~Framerate.playback` and :func:`~Framerate.timebase` only differ in
            NTSC framerates. All non-NTSC framerates will have identical values for
            both properties.
        """
        # If this is an NTSC timebase, convert to a rounded value over 1.
        if self._ntsc:
            return fractions.Fraction(round(self._value), 1)

        # Otherwise return our internal value.
        return self._value

    @property
    def ntsc(self) -> bool:
        """Whether this is an NTSC-style time base (aka 23.98, 24000/1001, etc)."""
        return self._ntsc

    @property
    def dropframe(self) -> bool:
        """Whether this Framerate is drop-frame."""
        return self._dropframe


def _validate_dropframe_ntsc(
    ntsc: Optional[bool],
    dropframe: bool,
) -> Tuple[bool, Optional[bool]]:
    """
    _validate_dropframe_ntsc validates that the drop frame and ntsc arguments are not
    in conflict and returns adjusted ones.
    """
    if dropframe:
        # If NTSC was explicitly set to False and dropframe was explicitly set to true
        # then there is a conflict.
        if ntsc is False:
            raise ValueError(
                "ntsc must be [True] or [None] if drop_frame is [True]",
            )

        # Otherwise if dropframe is true, NTSC must be set to true as well.
        ntsc = True

    return dropframe, ntsc


def _infer_ntsc(value: fractions.Fraction, ntsc: Optional[bool]) -> bool:
    """
    _infer_ntsc looks at the parsed fraction value and infers if it should be considered
    NTSC.
    """
    # If no explicit ntsc value was set, assume that values with a denominator of
    # 1001 are ntsc.
    if ntsc is None:
        if value.denominator == 1001:
            ntsc = True
        else:
            ntsc = False
    else:
        ntsc = ntsc

    return ntsc


def _validate_drop_frame_value(value: fractions.Fraction, dropframe: bool) -> None:
    """
    _validate_drop_frame_value validates that a framerate value with dropframe enabled
    is a multiple of 30000/1001.
    """
    # Validate that drop-frame TC is cleanly divisible by 30000/1001. Drop-frame is
    # not defined for any other timebases. Generally it is only allowed for 29.97
    # and 59.94
    if dropframe and value % fractions.Fraction(30000, 1001) != 0:
        raise ValueError(
            "drop_frame may only be true if framerate is divisible by "
            "30000/1001 (29.97)"
        )


def _parse(src: "FramerateSource", ntsc: Optional[bool]) -> fractions.Fraction:
    """_parse does the heavy lifting of parsing a value into a TimeBase."""
    if isinstance(src, str):
        frac = _parse_string(src, ntsc)
    elif isinstance(src, int):
        frac = fractions.Fraction(src, 1)
    elif isinstance(src, float):
        frac = _parse_float(src, ntsc)
    elif isinstance(src, tuple):
        if len(src) > 2:
            raise ValueError(
                f"Framerate tuple value must contain exactly 2 values, got "
                f"{len(src)}",
            )
        frac = fractions.Fraction(numerator=src[0], denominator=src[1])
    elif isinstance(src, Framerate):
        frac = src.playback
    elif isinstance(src, fractions.Fraction):
        frac = src
    else:
        raise TypeError(f"unsupported type for Framerate conversion: {type(src)}")

    # If the numerator is less than the denominator, swap the values.
    if frac.numerator < frac.denominator:
        frac = fractions.Fraction(
            numerator=frac.denominator,
            denominator=frac.numerator,
        )

    if ntsc:
        # If this is an ntsc timebase, we need to round up what we were given to the
        # nearest whole number and divide by 1001.
        frac = fractions.Fraction(round(frac) * 1000, 1001)

    return frac


def _parse_string(src: str, ntsc: Optional[bool]) -> fractions.Fraction:
    """
    _parse_string parses a string value to a fraction.Fraction and drop frame
    boolean.
    """
    # If this looks like a fraction (has a '/'), try to parse it as such.
    if "/" in src:
        return fractions.Fraction(src)

    # If this is a whole number like "24.0", we want to just strip it.
    if "." in src:
        try:
            src_float = float(src)
        except ValueError:
            pass
        else:
            return _parse_float(src_float, ntsc)

    # Try to parse as an int next.
    try:
        frac_int = int(src)
    except ValueError:
        raise ValueError(f"could not parse Framerate value of {repr(src)}")
    # If this int passed, return 1/[value] as the TimeBase
    return fractions.Fraction(numerator=1, denominator=frac_int)


def _parse_float(src: float, ntsc: Optional[bool]) -> fractions.Fraction:
    if not src.is_integer() and ntsc is False:
        raise ValueError(
            "non-whole-number floats values cannot be parsed when ntsc=False. "
            "use precise fraction.Fraction value instead",
        )

    # If this is an integer, returns [src]/1
    if src.is_integer():
        return fractions.Fraction(int(src))

    # Otherwise we are going to assume this in an NTSC-style rate (like 29.97), and
    # round up to the nearest whole number and use a denominator of 1001.
    return fractions.Fraction(round(src) * 1000, 1001)


FramerateSource = Union[Framerate, str, Tuple[int, int], fractions.Fraction, float]
"""FramerateSource is the set of types a Framerate can be created from"""


# We'll use a frozen dataclass for this so the values cannot be changed.
@dataclasses.dataclass(frozen=True)
class _Rates:
    """
    _Rates is used as a one-off na to hold a number of common pre-defined framerates for
    callers to use.
    """

    # 23.98 fps NTSC.
    F23_98: Framerate = Framerate(23.98, ntsc=True)

    # 24 fps.
    F24: Framerate = Framerate(24)

    # 29.97 fps NTSC.
    F29_97_NDF: Framerate = Framerate(29.97, ntsc=True)

    # 29.97 fps DROP FRAME.
    F29_97_DF: Framerate = Framerate(29.97, dropframe=True)

    # 30 fps NTSC.
    F30: Framerate = Framerate(30)

    # 47.95 fps NTSC.
    F47_95: Framerate = Framerate(47.95, ntsc=True)

    # 48 fps NTSC.
    F48: Framerate = Framerate(48)

    # 59.94 fps NTSC.
    F59_94_NDF: Framerate = Framerate(59.94, ntsc=True)

    # 59.94 fps NTSC DROP FRAME.
    F59_94_DF: Framerate = Framerate(59.94, dropframe=True)

    # 60 fps NTSC.
    F60: Framerate = Framerate(60)


RATE: _Rates = _Rates()
"""RATE holds a number of pre-defined frame rates for convenience"""
