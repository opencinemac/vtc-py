<h1 align="center">vtc-py</h1>
<p align="center">
    <img height=150 class="heightSet" align="center" src="https://raw.githubusercontent.com/opencinemac/vtc-py/master/zdocs/source/_static/logo1.svg"/>
</p>
<p align="center">A SMPTE Timecode Library for Python</p>
<p align="center">
    <a href="https://dev.azure.com/peake100/Open%20Cinema%20Collective/_build?definitionId=12"><img src="https://dev.azure.com/peake100/Open%20Cinema%20Collective/_apis/build/status/occlib-py?repoName=opencinemac%2Fvtc-py&branchName=dev" alt="click to see build pipeline"></a>
    <a href="https://dev.azure.com/peake100/Open%20Cinema%20Collective/_build?definitionId=12"><img src="https://img.shields.io/azure-devops/tests/peake100/Open%20Cinema%20Collective/12/dev?compact_message" alt="click to see build pipeline"></a>
    <a href="https://dev.azure.com/peake100/Open%20Cinema%20Collective/_build?definitionId=12"><img src="https://img.shields.io/azure-devops/coverage/peake100/Open%20Cinema%20Collective/12/dev?compact_message" alt="click to see build pipeline"></a>
</p>
<p align="center">
    <a href="https://codeclimate.com/github/opencinemac/vtc-py/maintainability"><img src="https://api.codeclimate.com/v1/badges/0d196b40c063b040cd21/maintainability" /></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>
</p>
<p align="center">
    <a href="https://github.com/opencinemac/vtc-py/"><img src="https://img.shields.io/pypi/pyversions/vtc" alt="Documentation"></a>
    <a href="https://pypi.org/project/vtc/"><img src="https://badge.fury.io/py/vtc.svg" alt="PyPI version" height="18"></a>
    <a href="https://opencinemac.github.io/vtc-py/"><img src="https://img.shields.io/badge/docs-github.io-blue" alt="Documentation"></a>
</p>

Overview
========

``vtc-py`` is inspired by years of scripting workflow solutions in a Hollywood cutting
room. It is designed to support both quick, one-off scripts and higher level production
code.

vtc aims to capture all the ways in which timecode is used throughout the industry so 
users can spend more time on their workflow logic, and less time handling the 
corner-cases of parsing and calculating timecode.

Features
--------

  - SMPTE Conventions:
    - [X] NTSC
    - [X] Drop-Frame
    - [ ] Interlaced timecode (not implemented)
  - Timecode Representations:
    - Timecode    | '01:00:00:00'
    - Frames      | 86400
    - Seconds     | 3600.0
    - Runtime     | '01:00:00.0'
    - Rational    | 18018/5
    - Feet+Frames | '5400+00'
      - [X] 35mm, 4-perf
      - [ ] 35mm, 3-perf
      - [ ] 35mm, 2-perf
      - [ ] 16mm
    - Premiere Ticks | 15240960000000
  - Operations:
    - Comparisons (==, <, <=, >, >=)
    - Add
    - Subtract
    - Scale (multiply and divide)
    - Divmod
    - Modulo
    - Negative
    - Absolute
    - Rebase (recalculate frame count at new framerate)
  - Flexible Parsing:
    - Partial timecodes      | '1:12'
    - Partial runtimes       | '1.5'
    - Negative string values | '-1:12', '-3+00'
    - Poorly formatted tc    | '1:13:4'
  - Type inference for fast scripting (add a tc string to a Timecode value).
  - Built-in consts for common framerates.
  - Modern Python Typehints for static analysis.

Demo
----

Let's take a quick high-level look at what you can do with this library:

```python
>>> import vtc

# It's easy to make a new 23.98 NTSC timecode.
>>> tc = vtc.Timecode("17:23:13:02", rate=23.98)

# We can get all sorts of ways to represent the timecode.
>>> tc.timecode
'17:23:13:02'

>>> tc.frames
1502234

>>> tc.seconds
Decimal('62655.67641666666666666666667')

>>> tc.rational
Fraction(751868117, 12000)

>>> tc.runtime(precision=3)
'17:24:15.676'

>>> tc.premiere_ticks
15915544300656000

>>> tc.feet_and_frames
'93889+10'

# Parsing is flexible
# Partial timecode
>>> vtc.Timecode("3:12", rate=23.98)
[00:00:03:12 @ [23.98 NTSC]]

# Frame count (ints)
>>> vtc.Timecode(24, rate=23.98)
[00:00:01:00 @ [23.98 NTSC]]

# Seconds (floats, decimals, or fractions)
>>> vtc.Timecode(1.5, rate=23.98)
[00:00:01:12 @ [23.98 NTSC]]

# Premiere ticks
>>> vtc.Timecode(vtc.PremiereTicks(254016000000), rate=23.98)
[00:00:01:00 @ [23.98 NTSC]]

# Feet + Frames
>>> vtc.Timecode("1+08", rate=23.98)
[00:00:01:00 @ [23.98 NTSC]]

# We can add two timecodes
>>> tc += vtc.Timecode("01:00:00:00", rate=23.98)
>>> tc
[18:23:13:02 @ [23.98 NTSC]]

# But if we want to do something quickly, we just use a timecode string instead.
>>> tc += "00:10:00:00"
>>> tc.timecode
'18:33:13:02'

# Adding ints means adding frames.
>>> tc += 2
>>> tc.timecode
'18:33:13:04'

# Adding floats, decimals, or fractions means adding seconds.
>>> tc += 1.5
>>> tc.timecode
'18:33:14:16'

# We can subtract too.
>>> tc -= "01:00:00:00"
>>> tc.timecode
'17:33:14:16'

# It's easy to compare two timecodes
>>> tc > vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98)
True

# Just like adding, we can use a shortcut and compare directly against a string
>>> "02:00:00:00" < tc
True

# Or against an int to check the frame count.
>>> vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98) == 86400
True

# It's easy to sort timecodes.
>>> sorted([tc, vtc.Timecode("03:00:00:00", rate=23.98)])
[[03:00:00:00 @ [23.98 NTSC]], [17:33:14:16 @ [23.98 NTSC]]]

# We can multiply
>>> tc *= 2
>>> tc.timecode
'35:06:29:08'

# ... divide ...
>>> tc /= 2
>>> tc.timecode
'17:33:14:16'

# ... and even get the remainder while dividing!
>>> dividend, remainder = divmod(tc, 3)
>>> dividend.timecode
'05:51:04:21'
>>> remainder.timecode
'00:00:00:01'

# Maybe just the remainder!
>>> remainder = tc % 3
>>> remainder.timecode
'00:00:00:01'

# We can make a timecode negative.
>>> tc = -tc
>>> tc.timecode
'-17:33:14:16'

# Or get it's absolute value.
>>> tc = abs(tc)
>>> tc.timecode
'17:33:14:16'

# We can make dropframe timecode for 29.97 or 59.94 using one of the pre-set
# framerates. We can use an int to parse 15000 frames.
>>> vtc.Timecode(15000, rate=vtc.RATE.F29_97_DF)
[00:08:20;18 @ [29.97 NTSC DF]]

# We can make new timecodes with arbitrary framerates if we want:
>>> vtc.Timecode("01:00:00:00", rate=240)
[01:00:00:00 @ [240]]

# Using a non-whole number indicates this is an NTSC timecode.
>>> vtc.Timecode("01:00:00:00", rate=239.76)
[01:00:00:00 @ [239.76 NTSC]]

# We can signal that we want a whole-frame timebase to be converted to an
# NTSC framerate.
>>> tc = vtc.Timecode("01:00:00:00", rate=vtc.Framerate(48, ntsc=True))
>>> tc
[01:00:00:00 @ [47.95 NTSC]]

# We can also rebase the frames using a new framerate!
>>> tc.rebase(vtc.RATE.F23_98)
[02:00:00:00 @ [23.98 NTSC]]

```



Goals
-----

- Parse and fetch all Timecode representations.
- A clean, Pythonic API.
- Support all operations that make sense for timecode.
- Sane shortcuts for scripting.

Non-Goals
---------

- Real-time timecode generators.

Installation
------------

```shell
pip install vtc
```

Getting Started
---------------

For full documentation:
[read the docs](https://opencinemac.github.io/vtc-py/).

For library development guide, 
[read the docs](https://opencinemac.github.io/occlib-py/).

Authors
-------

* **Billy Peake** - *Initial work*

Attributions
------------
<div>Drop-frame calculations adapted from <a href="https://www.davidheidelberger.com/2010/06/10/drop-frame-timecode/">David Heidelberger's blog.</a></div>
<div>Logo made by <a href="" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
