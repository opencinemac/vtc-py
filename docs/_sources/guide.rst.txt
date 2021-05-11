Intro
-----

vtc is built to have a simple, scriptable interface without sacrificing features or
correctness.

Let's walk through the assumptions vtc makes to offer a fast scripting API, and how
to override them.

Timecode: A History
-------------------

But first: what is timecode?

If you're already familiar with timecode, it's history, and it's flavors, feel free to
skip this section.

Back in the days of film, a running strip of numbers ran along the edge of the film
stock to uniquely identify each frame, called
`keycode <https://en.wikipedia.org/wiki/Keykode>`_.

Keycode was essential to the film editing process. The raw negative of a film is
irreplaceable: you loose quality each time you make a copy. Editing film is necessarily
a `destructive process <https://nofilmschool.com/2017/06/editing-on-a-flatbed>`_, and
often required multiple iterations. It would be just a tad nerve-wracking to take a pair
of scissors and some glue to the one-of-a-kind film reels straight out of the camera
on set, then running it over and over through a flatbed.

To avoid potential disaster, editors made their cut of the film using copies of the
raw negative, called a `work print <https://en.wikipedia.org/wiki/Workprint>`_, allowing
the editor to work without fear of sinking a project from slicing, dicing, and wearing
at the film.

When the edit was complete, it was necessary to know *exactly* where the edits had been
made, so it could be recreated with the raw negative for finishing. A *cut list* would
be written out, with the exact reels and keycodes for every cut, and would be used to
make an exact duplicate of the editor's work print with the mint condition raw negative.

In video and digital filmmaking, the same approach is used. Massive RAW files from a
RED, ARRI, Sony, or other cinema camera are rendered down to more manageable files an
Editor's machine won't choke on. Once the edit is complete, the raw files are
re-assembled using a digital cutlist on a powerful machine for finishing out the film.

In film, we referenced *keycode* to know exactly what frame was being displayed on
screen at any given time. In digital video, we reference the *timecode* of a given
frame.

For a technical deep-dive into the many flavors of timecode, check out
`Frame.io's <frame.io>`_
`excellent blogpost <https://blog.frame.io/2017/07/17/timecode-and-frame-rates/>`_ on
the subject.

Supplied Framerates
-------------------

vtc contains a number of pre-supplied framerates though the :py:data:`RATE` namespace:

    >>> import vtc
    >>> vtc.RATE.F23_98
    [23.98 NTSC]

Manual Framerate Creation
-------------------------

In order to make scripting more ergonomic, vtc has sane defaults for parsing Framerate
values.

By default, a whole-frame framerate is left as-is

.. doctest:: python

    >>> import vtc
    >>> vtc.Framerate(24)
    [24]

For floats too:

    >>> vtc.Framerate(24.0)
    [24]

It can be forced to an NTSC timebase by explicitly setting ``ntsc=True``.

    >>> vtc.Framerate(24, ntsc=True)
    [23.98 NTSC]

Non-whole-frame rates are interpreted as being NTSC by default:

    >>> vtc.Framerate(23.98)
    [23.98 NTSC]

.. warning::
    **NTSC Auto-detection**

    By default, non-whole framerates are rounded, multiplied by 1000, then put over a
    denominator of 1001 to make them proper NTSC framerates, regardless of their value.

    23.98 will be converted to 24000/1001, but so will 23.5.

We can disable interpretation of non-whole framerates as NTSC by setting ``ntsc=False``
in order to define custom rates.

    >>> import fractions
    >>> vtc.Framerate(fractions.Fraction(3, 2), ntsc=False)
    [1.5]

.. note::
    **Non-NTSC Restrictions**

    Using a float with ``ntsc=False`` will result in a ``ValueError``. Floats are not
    precise, and without the ntsc flag, vtc cannot know exactly what framerate you want.
    A ``decimal.Decimal`` or ``fractions.Fraction`` value must be used.

Drop-frame must be set specifically:

    >>> vtc.Framerate(29.97, dropframe=True)
    [29.97 NTSC DF]

.. note::
    **Dropframe Restrictions**

    Dropframe timecode may only be used on framerates that are a multiple of 30000/1001
    (29.97). The dropframe algorithm cannot be applied to any other timebase, as
    described in
    `this article <https://www.davidheidelberger.com/2010/06/10/drop-frame-timecode/>`_

Timecode Representations
------------------------

Timecode represents a specific frame of a video, and can be represented a number of
different ways. This section will give a brief overview of the representation attributes
:class:`vtc.Timecode` exposes, what they represent, and in what context you would
expect to see them.

Timecode
########

**property:** :func:`vtc.Timecode.timecode`

**what it is:** timecode is used as a human-readable way to represent the id of a given
frame. It is formatted to give a rough sense of where to find a frame:
[HOURS]:[MINUTES]:[SECONDS]:[FRAME]. For more on timecode, see Frame.io's
`excellent post <https://blog.frame.io/2017/07/17/timecode-and-frame-rates/>`_ on the
subject.

**where you see it:** Timecode is ubiquitous in video editing, a small sample of places
you might see timecode:

    - Source and Playback monitors in your favorite NLE.
    - Burned into the footage for dailies.
    - Cut lists like an EDL.

Frame Number
############

**property:** :func:`vtc.Timecode.frames`

**what it is:** frame number is the number of a frame if the timecode started at
00:00:00:00 and had been running until the current value. A timecode of '00:00:00:10'
has a frame number of 10. A timecode of '01:00:00:00' has a frame number of 86400.

**where you see it:**

    - Frame-sequence files: 'my_vfx_shot.0086400.exr'
    - FCP7XML cut lists:

        .. code-block:: xml

            <timecode>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
                <string>01:00:00:00</string>
                <frame>86400</frame>  <!-- <====THIS LINE-->
                <displayformat>NDF</displayformat>
            </timecode>

Seconds
#######

**property:** :func:`vtc.Timecode.frames`

**what it is:** the number of real-world seconds that have elapsed between 00:00:00:00
and the timecode value. With NTSC timecode, the timecode drifts from the real-world
elapsed time.

**where you see it:** Anywhere real-world time needs to be calculated.

Runtime
#######

**property:** :func:`vtc.Timecode.runtime`

**what it is:** the formatted version of seconds. It looks like timecode, but with a
decimal seconds value instead of a frame number place.

**where you see it:** Anywhere real-world time is used.

    - FFMPEG commands:

        .. code-block:: shell

            ffmpeg -ss 00:00:30.5 -i input.mov -t 00:00:10.25 output.mp4

Rational Time
#############

**property:** :func:`vtc.Timecode.rational`

**what it is:** the number of real-world seconds that have elapsed between 00:00:00:00
and the timecode value, expressed as a fraction.

**where you see it:** In code that needs to do lossless calculations of playback time
elapsed, but cannot rely on frame count, like adding two timecodes together with
different framerates.

    - `Open Timeline IO <https://github.com/PixarAnimationStudios/OpenTimelineIO>`_ uses
      rational time to track it's media playback.

Adobe Premiere Pro Ticks
########################

**property:** :func:`vtc.Timecode.premiere_ticks`

**what it is:** internally, Adobe Premiere Pro uses ticks to divide up a second, and
keep track of how far into that second we are. There are 254016000000 ticks in a second,
regardless of framerate in Premiere.

**where you see it:**

    - Premiere Pro Panel functions and scripts
    - FCP7XML cutlists generated from Premiere:

        .. code-block:: xml

            <clipitem id="clipitem-1">
                ...
                <in>158</in>
                <out>1102</out>
                <pproTicksIn>1673944272000</pproTicksIn>
                <pproTicksOut>11675231568000</pproTicksOut>
                ...
            </clipitem>

Feet And Frames
###############

**what it is:** On physical film, each foot contains a certain number of frames. For
35mm, 4-perf film (the most common type on Hollywood movies), this number is 16
frames per foot. Feet-And-Frames was often used in place of Keycode to quickly reference
a frame in the edit.

**where you see it:** For the most part, feet + frames has died out as a reference,
because digital media is not measured in feet. The most common place it is still used
is Studio Sound Departments. Many Sound Mixers and Designers intuitively think in
feet + frames, and it is often burned into the reference picture for them.

    - Sound turnover reference picture.
    - Sound turnover change lists.

Timecode Value Inferences
-------------------------

When creating a timecode or using operators, vtc.Timecode interprets other values
based on their type. This allows fast scripting by being able to use shorthand for
things like adding frames or seconds to a timecode without instantiating an entire
new :class:`Timecode` instance, like so:

    >>> tc = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98)
    >>> tc + "01:00:00:00"
    [02:00:00:00 @ [23.98 NTSC]]
    >>> tc + 12
    [01:00:00:12 @ [23.98 NTSC]]

In the first addition example, the timecode string is interpreted as a timecode. In
the second, our int value is interpreted as a frame count.

The below table details how types are interpreted by vtc when both instantiating new
Timecode instances and doing operations.

====================== =========================
Python Type            Interpreted As
====================== =========================
string ('HH:MM:SS:FF') Timecode
string ('HH:MM:SS.FF') Runtime
string ('FEET+FRAMES') Feet+Frames
int                    Frame Number
fractions.Fraction     Seconds
decimal.Decimal        Seconds
float                  Seconds
vtc.PremiereTicks      Adobe Premiere Pro Ticks
vtc.Timecode           value.rational as seconds
====================== =========================

Timecode Arithmetic
-------------------

The :class:`Timecode` type supports the following operations:

    - Addition
    - Subtraction
    - Multiplication
    - Division
    - Floor Division
    - Divmod
    - Modulo
    - Absolute Value
    - Negation

When two :class:`Timecode` values are involved in an operation together, the
framerate from the one on the left side is used. The real-world times of the timecodes
are added, then rounded to the nearest frame given the left-hand framerate.

    >>> vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24) + vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98)
    [02:00:03:14 @ [24]]

We might expect a result of 02:00:00:00 here, but because the real-time playback of
"01:00:00:00" at 23.98 NTSC is ~01:00:03:14, we get the result above.

Timecode Rounding
-----------------

Timecode is always rounded to the nearest complete frame when instantiating a new
:class:`Timecode` value. Partial frames are not accepted as this could result in
accumulated drift from imprecise calculations.

    >>> vtc.Timecode(fractions.Fraction(235, 240), rate=vtc.RATE.F24).rational
    Fraction(1, 1)

This applies to adding two timecodes together as well:

    >>> tc1 = vtc.Timecode(1, rate=vtc.RATE.F24)
    >>> tc2 = vtc.Timecode(1, rate=vtc.RATE.F30)
    >>>
    >>> tc1.rational
    Fraction(1, 24)
    >>>
    >>> tc2.rational
    Fraction(1, 30)
    >>>
    >>> tc3 = tc1 + tc2
    >>> tc3.rational
    Fraction(1, 12)

We assume that an NLE is not going to allow cuts to fall on fractional frames, and
adjust accordingly.

Timecode Comparison
-------------------

Timecode comparison is done based on real-world elapsed time, not frame count:

    >>> tc1 = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98)
    >>> tc2 = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24)
    >>>
    >>> tc1 == tc2
    False
    >>> tc1 > tc2
    True

This has implications for sorting:

    >>> sorted([tc1, tc2])
    [[01:00:00:00 @ [24]], [01:00:00:00 @ [23.98 NTSC]]]
