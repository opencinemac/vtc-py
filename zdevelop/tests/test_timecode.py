import decimal
import enum
import fractions
import vtc
import dataclasses
import unittest


@dataclasses.dataclass
class ParseTCCase:
    # The rate these values should be parsed at.
    rate: vtc.Framerate

    # Fractal seconds value to parse / expect.
    frac: fractions.Fraction = fractions.Fraction(0, 1)
    # Fractal int value to parse / expect.
    frames: int = 0
    # Timecode value to parse / expect.
    timecode: str = ""
    # Decimal seconds value to parse / expect.
    seconds: decimal.Decimal = decimal.Decimal(0)
    # Runtime value to parse / expect.
    runtime: str = ""

    class Source(enum.Enum):
        FRAC = enum.auto()
        FRAMES = enum.auto()
        TIMECODE = enum.auto()
        SECONDS = enum.auto()
        FLOAT = enum.auto()


class TestParsing(unittest.TestCase):
    def test_parse_timecode(self) -> None:
        sources = [
            ParseTCCase.Source.FRAC,
            ParseTCCase.Source.TIMECODE,
            ParseTCCase.Source.FRAMES,
            ParseTCCase.Source.SECONDS,
            ParseTCCase.Source.FLOAT,
        ]

        cases = [
            # 23.976 -----------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F23_98,
                frac=fractions.Fraction(18018, 5),
                frames=86400,
                timecode="01:00:00:00",
                seconds=decimal.Decimal("3603.6"),
                runtime="01:00:03.6",
            ),
            # 24 ---------------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=fractions.Fraction(3600, 1),
                frames=86400,
                timecode="01:00:00:00",
                seconds=decimal.Decimal(3600),
                runtime="01:00:00",
            ),
            # 29.97 DF ---------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(31031, 15000),
                frames=62,
                timecode="00:00:02;02",
                seconds=decimal.Decimal("2.068733333333333333333333333"),
                runtime="00:00:02.068733333",
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(3003, 50),
                frames=1800,
                timecode="00:01:00;02",
                seconds=decimal.Decimal("60.06"),
                runtime="00:01:00.06",
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(1800799, 15000),
                frames=3598,
                timecode="00:02:00;02",
                seconds=decimal.Decimal("120.0532666666666666666666667"),
                runtime="00:02:00.053266667",
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(2999997, 5000),
                frames=17982,
                timecode="00:10:00;00",
                seconds=decimal.Decimal("599.9994"),
                runtime="00:09:59.9994",
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(3300297, 5000),
                frames=19782,
                timecode="00:11:00;02",
                seconds=decimal.Decimal("660.0594"),
                runtime="00:11:00.0594",
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(8999991, 2500),
                frames=107892,
                timecode="01:00:00;00",
                seconds=decimal.Decimal("3599.9964"),
                runtime="00:59:59.9964",
            ),
        ]

        for case in cases:
            for source in sources:
                with self.subTest(f"{repr(case.timecode)} FROM: {source.name}"):
                    if source is ParseTCCase.Source.FRAC:
                        tc = vtc.Timecode(case.frac, case.rate)
                    elif source is ParseTCCase.Source.TIMECODE:
                        tc = vtc.Timecode(case.timecode, case.rate)
                    elif source is ParseTCCase.Source.FRAMES:
                        tc = vtc.Timecode(case.frames, case.rate)
                    elif source is ParseTCCase.Source.SECONDS:
                        tc = vtc.Timecode(case.seconds, case.rate)
                    elif source is ParseTCCase.Source.FLOAT:
                        tc = vtc.Timecode(float(case.seconds), case.rate)
                    else:
                        raise RuntimeError("source not known for test case")

                    print()
                    print("RATE:", repr(tc.rate))
                    print("TC:", tc.timecode)
                    print("FRAMES:", tc.frames)
                    print("SECONDS:", tc.seconds)
                    print("RATIONAL:", tc.frac)

                    self.assertEqual(tc.frac, case.frac, "parsed rational expected")
                    self.assertEqual(
                        tc.frames,
                        case.frames,
                        msg="parsed frames expected",
                    )
                    self.assertEqual(
                        tc.timecode,
                        case.timecode,
                        msg="parsed timecode expected",
                    )
                    self.assertEqual(
                        tc.seconds,
                        case.seconds,
                        msg="parsed seconds expected",
                    )
                    self.assertEqual(
                        tc.runtime(),
                        case.runtime,
                        msg="parsed runtime expected",
                    )
