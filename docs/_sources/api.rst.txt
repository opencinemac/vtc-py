.. automodule:: vtc

    The vtc module contains types for working with SMPTE and arbitrary timecode.

Timecode
--------

.. autoclass:: Timecode
    :members:

Framerate
---------

.. autoclass:: Framerate
    :members:

RATE
----

.. py:data:: RATE

    Rate contains a number of pre-defined, common framerates for ease-of-use

    ========== =========== ===== ==========
    Attribute  Framerate   NTSC  DROP FRAME
    ========== =========== ===== ==========
    F23_98     24000/1001  True  False
    F24        24/1        False False
    F29_97_NDF 30000/1001  True  False
    F29_97_DF  30000/1001  True  True
    F30        30/1        False False
    F47_95     40000/1001  True  False
    F48        48/1        False False
    F59_94_NDF 60000/1001  True  False
    F59_94_DF  60000/1001  True  True
    F60        60/1        False True
    ========== =========== ===== ==========

PremiereTicks
-------------

.. autoclass:: PremiereTicks
    :members: