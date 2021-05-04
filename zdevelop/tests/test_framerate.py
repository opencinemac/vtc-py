import collections
import dataclasses
import fractions
import unittest
import vtc
from typing import Optional, Type, Union, Tuple, List, NamedTuple


# We'll use this to set up our test cases.
@dataclasses.dataclass
class FramerateParseCase:
    source: Union[vtc.FramerateSource, bytes, Tuple[int, int, int]]

    ntsc_arg: Optional[bool] = None

    expected_frac: Optional[fractions.Fraction] = None
    expected_drop_frame: bool = False
    expected_ntsc: bool = False

    expected_error: Optional[Type[BaseException]] = None
    expected_error_text: str = ""

    def __str__(self) -> str:
        return f"{repr(self.source)} -> {self.expected_frac}"


class TestTimebaseBasics(unittest.TestCase):
    def test_timebase_parse(self) -> None:
        cases = [
            # 23.976 ---------
            # ----------------
            FramerateParseCase(
                source="23.976",
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=23.976,
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="23.98",
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=23.98,
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(24000, 1001),
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(1001, 24000),
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(24000, 1001),
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(1001, 24000),
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="24000/1001",
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="1001/24000",
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=vtc.Framerate("24000/1001"),
                expected_frac=fractions.Fraction(24000, 1001),
                expected_ntsc=True,
            ),
            # 24.0 -----------
            # ----------------
            FramerateParseCase(
                source="24.0",
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=24.0,
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source="24",
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=24,
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(24, 1),
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(1, 24),
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=(24, 1),
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=(1, 24),
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source="24/1",
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source="1/24",
                expected_frac=fractions.Fraction(24, 1),
            ),
            FramerateParseCase(
                source=vtc.Framerate("24/1"),
                expected_frac=fractions.Fraction(24, 1),
            ),
            # 29.97 ----------
            # ----------------
            FramerateParseCase(
                source="29.97",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=29.97,
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="29.97",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="29.97",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="29.97",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_drop_frame=True,
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="29.97",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_drop_frame=True,
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(30000, 1001),
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(1001, 30000),
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(30000, 1001),
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(1001, 30000),
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="30000/1001",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="1001/30000",
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=vtc.Framerate("30000/1001"),
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=True,
            ),
            # Passing an explicit false to ntsc should lead to a false result.
            FramerateParseCase(
                source="30000/1001",
                ntsc_arg=False,
                expected_frac=fractions.Fraction(30000, 1001),
                expected_ntsc=False,
            ),
            # 30.0 -----------
            # ----------------
            FramerateParseCase(
                source="30",
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(
                source=30,
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(
                source="30.0",
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(
                source=30.0,
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(30, 1),
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(1, 30),
                expected_frac=fractions.Fraction(30, 1),
            ),
            FramerateParseCase(source=(30, 1), expected_frac=fractions.Fraction(30, 1)),
            FramerateParseCase(source=(1, 30), expected_frac=fractions.Fraction(30, 1)),
            FramerateParseCase(source="30/1", expected_frac=fractions.Fraction(30, 1)),
            FramerateParseCase(source="1/30", expected_frac=fractions.Fraction(30, 1)),
            FramerateParseCase(
                source=vtc.Framerate("30/1"), expected_frac=fractions.Fraction(30, 1)
            ),
            # 47.95 ----------
            # ----------------
            FramerateParseCase(
                source="47.95",
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=47.95,
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(48000, 1001),
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(1001, 48000),
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(48000, 1001),
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(1001, 48000),
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="48000/1001",
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="1001/48000",
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=vtc.Framerate("48000/1001"),
                expected_frac=fractions.Fraction(48000, 1001),
                expected_ntsc=True,
            ),
            # 48.0 -----------
            # ----------------
            FramerateParseCase(
                source="48",
                expected_frac=fractions.Fraction(48, 1),
            ),
            FramerateParseCase(
                source=48,
                expected_frac=fractions.Fraction(48, 1),
            ),
            FramerateParseCase(
                source=48.0,
                expected_frac=fractions.Fraction(48, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(48, 1),
                expected_frac=fractions.Fraction(48, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(1, 48),
                expected_frac=fractions.Fraction(48, 1),
            ),
            FramerateParseCase(source=(48, 1), expected_frac=fractions.Fraction(48, 1)),
            FramerateParseCase(source=(1, 48), expected_frac=fractions.Fraction(48, 1)),
            FramerateParseCase(source="48/1", expected_frac=fractions.Fraction(48, 1)),
            FramerateParseCase(source="1/48", expected_frac=fractions.Fraction(48, 1)),
            FramerateParseCase(
                source=vtc.Framerate("48/1"), expected_frac=fractions.Fraction(48, 1)
            ),
            # 59.94 ----------
            # ----------------
            FramerateParseCase(
                source="59.94",
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=59.94,
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(60000, 1001),
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(1001, 60000),
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(60000, 1001),
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(1001, 60000),
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="60000/1001",
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="1001/60000",
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=vtc.Framerate("60000/1001"),
                expected_frac=fractions.Fraction(60000, 1001),
                expected_ntsc=True,
            ),
            # 60.0 -----------
            # ----------------
            FramerateParseCase(
                source="60",
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(
                source=60,
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(
                source="60.0",
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(
                source=60.0,
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(60, 1),
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(1, 60),
                expected_frac=fractions.Fraction(60, 1),
            ),
            FramerateParseCase(source=(60, 1), expected_frac=fractions.Fraction(60, 1)),
            FramerateParseCase(source=(1, 60), expected_frac=fractions.Fraction(60, 1)),
            FramerateParseCase(source="60/1", expected_frac=fractions.Fraction(60, 1)),
            FramerateParseCase(source="1/60", expected_frac=fractions.Fraction(60, 1)),
            FramerateParseCase(
                source=vtc.Framerate("60/1"), expected_frac=fractions.Fraction(60, 1)
            ),
            # 199.88 ---------
            # ----------------
            FramerateParseCase(
                source="119.88",
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=119.88,
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(120000, 1001),
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=fractions.Fraction(1001, 120000),
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(120000, 1001),
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=(1001, 120000),
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="120000/1001",
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source="1001/120000",
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            FramerateParseCase(
                source=vtc.Framerate("120000/1001"),
                expected_frac=fractions.Fraction(120000, 1001),
                expected_ntsc=True,
            ),
            # 120.0 -----------
            # ----------------
            FramerateParseCase(
                source="120",
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source=120,
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source="120.0",
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source=120.0,
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(120, 1),
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source=fractions.Fraction(1, 120),
                expected_frac=fractions.Fraction(120, 1),
            ),
            FramerateParseCase(
                source=(120, 1), expected_frac=fractions.Fraction(120, 1)
            ),
            FramerateParseCase(
                source=(1, 120), expected_frac=fractions.Fraction(120, 1)
            ),
            FramerateParseCase(
                source="120/1", expected_frac=fractions.Fraction(120, 1)
            ),
            FramerateParseCase(
                source="1/120", expected_frac=fractions.Fraction(120, 1)
            ),
            FramerateParseCase(
                source=vtc.Framerate("120/1"), expected_frac=fractions.Fraction(120, 1)
            ),
            # ERRORS ----------
            # -----------------
            FramerateParseCase(
                source="Not A FrameRate",
                expected_error=ValueError,
                expected_error_text=(
                    "could not parse Framerate value of 'Not A FrameRate'"
                ),
            ),
            FramerateParseCase(
                source=(24, 1, 0),
                expected_error=ValueError,
                expected_error_text=(
                    "Framerate tuple value must contain exactly 2 values, got 3"
                ),
            ),
            FramerateParseCase(
                source=b"not a string",
                expected_error=TypeError,
                expected_error_text=(
                    "unsupported type for Framerate conversion: <class 'bytes'>"
                ),
            ),
            FramerateParseCase(
                source="not.afloat",
                expected_error=ValueError,
                expected_error_text="could not parse Framerate value of 'not.afloat'",
            ),
            FramerateParseCase(
                source=29.97,
                ntsc_arg=False,
                expected_drop_frame=True,
                expected_error=ValueError,
                expected_error_text=(
                    "ntsc must be [True] or [None] if drop_frame is [True]"
                ),
            ),
            FramerateParseCase(
                source=29.97,
                ntsc_arg=False,
                expected_error=ValueError,
                expected_error_text=(
                    "non-whole-number floats values cannot be parsed when ntsc=False. "
                    "use precise fraction.Fraction value instead"
                ),
            ),
        ]

        for case in cases:
            with self.subTest(str(case)):
                if case.expected_error is not None:
                    with self.assertRaises(case.expected_error) as err:
                        vtc.Framerate(
                            case.source,  # type: ignore
                            ntsc=case.ntsc_arg,
                            drop_frame=case.expected_drop_frame,
                        )

                    self.assertEqual(
                        str(err.exception),
                        case.expected_error_text,
                        "error message text expected",
                    )
                    continue

                tb = vtc.Framerate(
                    case.source,  # type: ignore
                    ntsc=case.ntsc_arg,
                    drop_frame=case.expected_drop_frame,
                )

                print("\nPARSED:", tb)
                self.assertEqual(tb.frac, case.expected_frac, "frac value is expected")
                self.assertEqual(
                    tb.drop_frame,
                    case.expected_drop_frame,
                    "drop frame is expected",
                )
                self.assertEqual(tb.ntsc, case.expected_ntsc, "ntsc value is expected")

    def test_parse_drop_frame(self) -> None:
        fr = vtc.Framerate(29.97, drop_frame=True)
        self.assertEqual(fr.frac, fractions.Fraction(30000, 1001), "tb frac expected")
        self.assertTrue(fr.drop_frame, "tb is drop frame")

    def test_parse_error_drop_frame_bad_value(self) -> None:
        with self.assertRaises(ValueError) as error:
            vtc.Framerate(23.98, drop_frame=True)

        self.assertEqual(
            str(error.exception),
            "drop_frame may only be true if framerate is divisible by "
            "30000/1001 (29.97)",
            "error message expected",
        )

    def test_repr(self) -> None:
        class Case(NamedTuple):
            value: vtc.Framerate
            expected: str

        cases: List[Case] = [
            Case(vtc.Framerate(24), "[24 fps]"),
            Case(vtc.Framerate(29.97, ntsc=True), "[29.97 fps NTSC]"),
            Case(vtc.Framerate(29.97, drop_frame=True), "[29.97 fps NTSC DF]"),
        ]

        for case in cases:
            with self.subTest(str(case.value)):
                self.assertEqual(repr(case.value), case.expected)

    def test_equality(self) -> None:
        class Case(NamedTuple):
            fr1: vtc.Framerate
            fr2: vtc.Framerate
            equal: bool

        cases: List[Case] = [
            Case(vtc.Framerate(23.98), vtc.Framerate(23.98), True),
            Case(vtc.Framerate(23.98), vtc.Framerate("24000/1001"), True),
            Case(vtc.Framerate(23.98), vtc.Framerate("24000/1001", ntsc=False), False),
            Case(vtc.Framerate(23.98), vtc.Framerate(29.97), False),
            Case(vtc.Framerate(29.97, drop_frame=True), vtc.Framerate(29.97), False),
        ]

        for case in cases:
            with self.subTest(f"{repr(case.fr1)} == {repr(case.fr2)} | {case.equal}"):
                self.assertEqual(case.equal, case.fr1 == case.fr2, "check equality")
