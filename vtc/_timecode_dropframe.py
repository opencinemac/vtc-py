import fractions

from ._framerate import Framerate
from ._timecode_sections import TimecodeSections


def _parse_drop_frame_adjustment(
    sections: TimecodeSections,
    rate: Framerate,
) -> fractions.Fraction:
    """
    _parse_drop_frame adjusts the frame number based on drop-frame TC conventions.

    Algorithm adapted from:
    https://www.davidheidelberger.com/2010/06/10/drop-frame-timecode/
    """
    timebase = rate.timebase
    drop_frames = round(timebase * 0.066666)

    # We have a bad frame value if our 'frames' place is less than the drop_frames we
    # skip on minutes not divisible by 10.
    has_bad_frame = sections.frames < drop_frames
    is_tenth_minute = sections.minutes % 10 == 0 or sections.minutes == 0
    if has_bad_frame and not is_tenth_minute:
        raise ValueError(
            f"drop-frame tc cannot have a frames value of less than {drop_frames} on "
            f"minutes not divisible by 10, found '{sections.frames}'",
        )

    total_minutes = 60 * sections.hours + sections.minutes
    adjustment = drop_frames * (total_minutes - total_minutes // 10)

    return -fractions.Fraction(adjustment, 1)


def _frame_num_to_drop_frame_num(
    frame_number: int,
    timebase: fractions.Fraction,
) -> int:
    """
    _frame_num_to_drop_frame_num converts a frame-number to an adjusted frame number for
    creating drop-frame tc.

    Algorithm adapted from:
    https://www.davidheidelberger.com/2010/06/10/drop-frame-timecode/

    :param frame_number: the frame number to convert to a drop-frame number.
    :param timebase: the timebase (not playback) to use for the conversion.

    :returns: The frame number adjusted to produce the correct drop-frame timecode when
    used in the normal timecode calculation.
    """
    # Get the number frames-per-minute at the whole-frame rate
    frames_per_minute_whole = timebase * 60
    # Get the number of frames we need to drop each time we drop frames (ex: 2 or 29.97)
    drop_frames = round(timebase * 0.066666)

    # Get the number of frames are in a minute where we have dropped frames at the
    # beginning
    frames_per_minute_drop = (timebase * 60) - drop_frames
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
    frames -= timebase
    adjustment += drop_frames

    # Get the number of remaining drop-minutes present, and add a drop adjustment for
    # each
    minutes_drop = frames // frames_per_minute_drop
    adjustment += minutes_drop * drop_frames

    # Return our original frame number adjusted by our calculated adjustment.
    return frame_number + adjustment
