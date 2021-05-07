import fractions
import re

# _tc_regex is the regex pattern for parsing a timecode string (ex: '01:00:00:00').
_tc_regex: re.Pattern = re.compile(
    r"(?P<negative>-)?"
    r"((?P<section1>[0-9]+)[:|;])?((?P<section2>[0-9]+)[:|;])?"
    r"((?P<section3>[0-9]+)[:|;])?(?P<frames>[0-9]+)$"
)

# _runtime_regex is the regex pattern for parsing a runtime string (ex: '01:00:00.0')
_runtime_regex: re.Pattern = re.compile(
    r"(?P<negative>-)?"
    r"((?P<section1>[0-9]+)[:|;])?((?P<section2>[0-9]+)[:|;])?"
    r"(?P<seconds>[0-9]+(\.[0-9]+)?)$"
)

# _feet_and_frames_regex is the regex patter for matching a feet and frames string
# (ex: 5400+13)
_feet_and_frames_regex: re.Pattern = re.compile(
    r"(?P<negative>-)?" r"(?P<feet>[0-9]+)" r"\+(?P<frames>[0-9]+)",
)

# Cache the number of seconds in a minute and hour.
_SECONDS_PER_MINUTE: int = 60
_SECONDS_PER_HOUR: int = 3600

# _PPRO_TICKS_PER_SECOND is the number of Adobe Premiere Pro ticks in a second. This
# value is constant regardless of framerate.
_PPRO_TICKS_PER_SECOND: fractions.Fraction = fractions.Fraction(254016000000, 1)

# _FRAMES_PER_FOOT is the number of frames in a foot of 35mm, 4-perf film.
_FRAMES_PER_FOOT: int = 16
