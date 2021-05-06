import decimal
import enum
import fractions
import vtc
import dataclasses
import unittest
from typing import Tuple, NamedTuple, List, Union, Optional

from zdevelop.tests.conftest import MANY_BASIC_EDITS_DATA, TableTimecodeInfo


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

    @classmethod
    def from_table_info(cls, event: TableTimecodeInfo) -> "ParseTCCase":
        return cls(
            rate=vtc.Framerate(
                event.frame_rate_frac,
                ntsc=event.ntsc,
                drop_frame=event.drop_frame,
            ),
            frac=event.seconds_rational,
            frames=event.frame,
            timecode=event.timecode,
            seconds=event.seconds_decimal,
            runtime=event.runtime,
        )


class TestParse(unittest.TestCase):
    def test_parse_timecode(self) -> None:
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
            ParseTCCase(
                rate=vtc.RATE.F23_98,
                frac=fractions.Fraction(12012, 5),
                frames=57600,
                timecode="00:40:00:00",
                seconds=decimal.Decimal("2402.4"),
                runtime="00:40:02.4",
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
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=fractions.Fraction(2400, 1),
                frames=57600,
                timecode="00:40:00:00",
                seconds=decimal.Decimal("2400.0"),
                runtime="00:40:00",
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
            self._run_case(case)

    def test_parse_overflows(self) -> None:
        """tests that we parse timecodes with overflowed positions correctly"""

        class TestCase(NamedTuple):
            str_in: str
            str_out: str

        cases: List[TestCase] = [
            TestCase(
                "00:59:59:24",
                "01:00:00:00",
            ),
            TestCase(
                "00:59:59:28",
                "01:00:00:04",
            ),
            TestCase(
                "00:00:62:04",
                "00:01:02:04",
            ),
            TestCase(
                "00:62:01:04",
                "01:02:01:04",
            ),
            TestCase(
                "00:62:62:04",
                "01:03:02:04",
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.str_in} -> {case.str_out}"):
                tc = vtc.Timecode(case.str_in, vtc.RATE.F24)
                self.assertEqual(case.str_out, tc.timecode)

    def test_parse_unsupported_type(self) -> None:
        with self.assertRaises(TypeError) as caught:
            vtc.Timecode(dict(), vtc.RATE.F24)  # type: ignore

        self.assertEqual(
            "unsupported type for Timecode conversion: <class 'dict'>",
            str(caught.exception),
        )

    def test_parse_bad_string(self) -> None:
        with self.assertRaises(ValueError) as caught:
            vtc.Timecode("notatimecode", vtc.RATE.F24)  # type: ignore

        self.assertEqual(
            "'notatimecode' is not a timecode string",
            str(caught.exception),
        )

    def test_invalid_drop_frame_value(self) -> None:
        with self.assertRaises(ValueError) as caught:
            vtc.Timecode("00:01:00:00", vtc.RATE.F29_97_DF)  # type: ignore

        self.assertEqual(
            "drop-frame tc cannot have a frames value of 0 on minutes not divisible by "
            "10",
            str(caught.exception),
        )

    def _run_case(self, case: ParseTCCase, name: str = "") -> None:
        sources = [
            ParseTCCase.Source.FRAC,
            ParseTCCase.Source.TIMECODE,
            ParseTCCase.Source.FRAMES,
            ParseTCCase.Source.SECONDS,
            ParseTCCase.Source.FLOAT,
        ]

        for source in sources:
            sub_name = ""
            if name != "":
                sub_name = name + ": "
            sub_name += f"{repr(case.timecode)} FROM: {source.name}"

            with self.subTest(sub_name):
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

                self.assertEqual(
                    tc.timecode,
                    case.timecode,
                    msg=f"parsed timecode expected with rate {repr(tc.rate)}",
                )
                self.assertEqual(tc.frac, case.frac, "parsed rational expected")
                self.assertEqual(
                    tc.frames,
                    case.frames,
                    msg="parsed frames expected",
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

    def test_parse_timeline_tc(self) -> None:
        for i, event in enumerate(MANY_BASIC_EDITS_DATA.events):
            rec_in = ParseTCCase.from_table_info(event.record_in)
            self._run_case(rec_in, name=f"EVENT {str(i).zfill(3)} REC IN")

            rec_out = ParseTCCase.from_table_info(event.record_out)
            self._run_case(rec_out, name=f"EVENT {str(i).zfill(3)} REC OUT")

            src_in = ParseTCCase.from_table_info(event.source_in)
            self._run_case(src_in, name=f"EVENT {str(i).zfill(3)} SRC IN")

            src_out = ParseTCCase.from_table_info(event.source_out)
            self._run_case(src_out, name=f"EVENT {str(i).zfill(3)} SRC OUT")


class TestDunderMethods(unittest.TestCase):
    def test_compare(self) -> None:
        class TestCase(NamedTuple):
            tc1: vtc.Timecode
            tc2: vtc.TimecodeSource
            eq: bool
            lt: bool
            gt: bool

        cases: List[TestCase] = [
            # 24 FPS ----------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=vtc.Timecode("00:59:59:24", vtc.RATE.F24),
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=vtc.Timecode("02:00:00:00", vtc.RATE.F24),
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=vtc.Timecode("01:00:00:01", vtc.RATE.F24),
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=vtc.Timecode("00:59:59:23", vtc.RATE.F24),
                eq=False,
                lt=False,
                gt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=86400,
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=86399,
                eq=False,
                lt=False,
                gt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=fractions.Fraction(3600, 1),
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=3600.0,
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=decimal.Decimal("3600.0"),
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                tc2=fractions.Fraction(3600, 1),
                eq=True,
                lt=False,
                gt=False,
            ),
            # 23.98 --------------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=decimal.Decimal("3603.6"),
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=3603.6,
                eq=True,
                lt=False,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:01", vtc.RATE.F23_98),
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=86401,
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=vtc.Timecode(86401, vtc.RATE.F23_98),
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("00:00:00:00", vtc.RATE.F23_98),
                tc2=vtc.Timecode("02:00:00:00", vtc.RATE.F23_98),
                eq=False,
                lt=True,
                gt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("00:00:00:00", vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                eq=False,
                lt=True,
                gt=False,
            ),
            # Mixed ---------------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                eq=False,
                lt=False,
                gt=True,
            ),
        ]

        for case in cases:
            # For each case we are going to flip the values and expectations to make
            # sure comparisons between different types work in both directions.

            test_name = f"{repr(case.tc1)} == {repr(case.tc2)} is {case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.eq, case.tc1 == case.tc2, test_name)

            test_name = f"{repr(case.tc2)} == {repr(case.tc1)} is {case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.eq, case.tc2 == case.tc1, test_name)

            test_name = f"{repr(case.tc1)} < {repr(case.tc2)} is {case.lt}"
            with self.subTest(test_name):
                self.assertEqual(case.lt, case.tc1 < case.tc2, test_name)

            test_name = (
                f"{repr(case.tc2)} < {repr(case.tc1)} is {not case.lt and not case.eq}"
            )
            with self.subTest(test_name):
                self.assertEqual(
                    not case.lt and not case.eq,
                    case.tc2 < case.tc1,
                    test_name,
                )

            test_name = f"{repr(case.tc1)} <= {repr(case.tc2)} is {case.lt or case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.lt or case.eq, case.tc1 <= case.tc2, test_name)

            test_name = (
                f"{repr(case.tc2)} <= {repr(case.tc1)} is {not case.lt or case.eq}"
            )
            with self.subTest(test_name):
                self.assertEqual(not case.lt or case.eq, case.tc2 <= case.tc1)

            test_name = f"{repr(case.tc1)} > {repr(case.tc2)} is {case.gt}"
            with self.subTest(test_name):
                self.assertEqual(case.gt, case.tc1 > case.tc2, test_name)

            test_name = (
                f"{repr(case.tc1)} > {repr(case.tc2)} is {not case.gt and not case.eq}"
            )
            with self.subTest(test_name):
                self.assertEqual(
                    not case.gt and not case.eq,
                    case.tc2 > case.tc1,
                    test_name,
                )

            test_name = f"{repr(case.tc1)} > {repr(case.tc2)} is {case.gt or case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.gt or case.eq, case.tc1 >= case.tc2, test_name)

            test_name = (
                f"{repr(case.tc2)} > {repr(case.tc1)} is {not case.gt or case.eq}"
            )
            with self.subTest(test_name):
                self.assertEqual(
                    not case.gt or case.eq,
                    case.tc2 >= case.tc1,
                    test_name,
                )

    def test_compare_not_implemented(self) -> None:
        self.assertNotEqual(
            vtc.Timecode("01:00:00:00", vtc.RATE.F24),
            dict(),
            "unsupported type not equal",
        )

    def test_sort_timecodes(self) -> None:
        class TestCase(NamedTuple):
            tcs_in: List[vtc.Timecode]
            tcs_out: List[vtc.Timecode]

        cases: List[TestCase] = [
            TestCase(
                tcs_in=[
                    vtc.Timecode("00:01:00:00", vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                    vtc.Timecode("00:00:10:00", vtc.RATE.F23_98),
                ],
                tcs_out=[
                    vtc.Timecode("00:00:10:00", vtc.RATE.F23_98),
                    vtc.Timecode("00:01:00:00", vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                ],
            )
        ]

        for i, case in enumerate(cases):
            with self.subTest(i):
                sorted_timecodes = sorted(case.tcs_in)
                self.assertListEqual(case.tcs_out, sorted_timecodes, "sorted correctly")

    def test_multiply(self) -> None:
        class TestCase(NamedTuple):
            tc_in: vtc.Timecode
            multiplier: Union[int, float, decimal.Decimal, fractions.Fraction]
            expected: vtc.Timecode

        cases: List[TestCase] = [
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                multiplier=2,
                expected=vtc.Timecode("02:00:00:00", vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                multiplier=2,
                expected=vtc.Timecode("02:00:00:00", vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                multiplier=1.5,
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                multiplier=1.5,
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                multiplier=fractions.Fraction(3, 2),
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                multiplier=fractions.Fraction(3, 2),
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                multiplier=decimal.Decimal("1.5"),
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                multiplier=decimal.Decimal("1.5"),
                expected=vtc.Timecode("01:30:00:00", vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                multiplier=0.5,
                expected=vtc.Timecode("00:30:00:00", vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                multiplier=0.5,
                expected=vtc.Timecode("00:30:00:00", vtc.RATE.F23_98),
            ),
        ]

        for case in cases:
            name = f"{case.tc_in} * {case.multiplier} = {case.expected}"
            with self.subTest(name):
                result = case.tc_in * case.multiplier
                self.assertEqual(case.expected, result, name)

    def test_divmod(self) -> None:
        class TestCase(NamedTuple):
            source: vtc.Timecode
            divisor: Union[int, float, decimal.Decimal, fractions.Fraction]
            expected_dividend: vtc.Timecode
            expected_modulo: vtc.Timecode
            expected_truediv: Optional[vtc.Timecode] = None

        cases: List[TestCase] = [
            TestCase(
                source=vtc.Timecode("01:00:00:00", vtc.RATE.F24),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:00", vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:00", vtc.RATE.F23_98),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:00", vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F24),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F23_98),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F24),
                divisor=4,
                expected_dividend=vtc.Timecode("00:15:00:00", vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F23_98),
                divisor=4,
                expected_dividend=vtc.Timecode("00:15:00:00", vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F24),
                divisor=1.5,
                expected_dividend=vtc.Timecode("00:40:00:00", vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F24),
                expected_truediv=vtc.Timecode("00:40:00:01", vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", vtc.RATE.F23_98),
                divisor=1.5,
                expected_dividend=vtc.Timecode("00:40:00:00", vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", vtc.RATE.F23_98),
                expected_truediv=vtc.Timecode("00:40:00:01", vtc.RATE.F23_98),
            ),
        ]

        for case in cases:
            name = (
                f"divmod({repr(case.source)}, {case.divisor})"
                f" = {case.expected_dividend}, {case.expected_modulo}"
            )
            with self.subTest(name):
                dividend, modulo = divmod(case.source, case.divisor)
                self.assertEqual(
                    case.expected_dividend,
                    dividend,
                    f"dividend of divmod({case.source}, {case.divisor})",
                )

                self.assertEqual(
                    case.expected_modulo,
                    modulo,
                    f"modulo of divmod({case.source}, {case.divisor})",
                )

            expected_truediv = case.expected_dividend
            if case.expected_truediv is not None:
                expected_truediv = case.expected_truediv
            name = f"{repr(case.source)} / {case.divisor} = {expected_truediv}"
            with self.subTest(name):
                dividend = case.source / case.divisor
                self.assertEqual(
                    expected_truediv,
                    dividend,
                    name,
                )

            name = f"{repr(case.source)} // {case.divisor} = {case.expected_dividend}"
            with self.subTest(name):
                dividend = case.source // case.divisor
                self.assertEqual(
                    case.expected_dividend,
                    dividend,
                    name,
                )

            name = f"{repr(case.source)} % {case.divisor} = {case.expected_modulo}"
            with self.subTest(name):
                modulo = case.source % case.divisor
                self.assertEqual(
                    case.expected_modulo,
                    modulo,
                    name,
                )

    def test_timeline_addition(self) -> None:
        """
        This test adds up all of the events in a timeline with no blank spots and
        ensures our running TC and event length continuously match what was reported
        in an EDL and XML combo generated by Premiere. By checking against an outside
        implementation, we raise confidence in the correctness of our calculations, and
        by running a against a multi-hundred event sequence, we ensure high coverage of
        pseudo-random timecodes.

        This sequence is in 23.98. In the future, we should probably add additional
        frame rates and even mixed rates.
        """
        seq_framerate = vtc.Framerate(
            MANY_BASIC_EDITS_DATA.start_time.timebase,
            ntsc=MANY_BASIC_EDITS_DATA.start_time.ntsc,
            drop_frame=MANY_BASIC_EDITS_DATA.start_time.drop_frame,
        )

        rec_total_duration = vtc.Timecode(0, seq_framerate)
        rec_tc_out = vtc.Timecode(
            MANY_BASIC_EDITS_DATA.events[0].record_in.timecode,
            seq_framerate,
        )

        src_total_duration = vtc.Timecode(rec_total_duration, rec_total_duration.rate)
        src_tc_out = vtc.Timecode(
            MANY_BASIC_EDITS_DATA.events[0].record_in.timecode,
            seq_framerate,
        )

        for i, event in enumerate(MANY_BASIC_EDITS_DATA.events):
            with self.subTest(f"Event {i} Parse"):
                rec_in_info = ParseTCCase.from_table_info(event.record_in)
                rec_in = vtc.Timecode(rec_in_info.timecode, rec_in_info.rate)

                rec_out_info = ParseTCCase.from_table_info(event.record_out)
                rec_out = vtc.Timecode(rec_out_info.timecode, rec_out_info.rate)

                src_in_info = ParseTCCase.from_table_info(event.source_in)
                src_in = vtc.Timecode(src_in_info.timecode, src_in_info.rate)

                src_out_info = ParseTCCase.from_table_info(event.source_out)
                src_out = vtc.Timecode(src_out_info.timecode, src_out_info.rate)

            with self.subTest(f"Event {i} Source Length"):
                src_total_duration, src_tc_out = self.check_running_event(
                    event_in=src_in,
                    event_out=src_out,
                    current_total=src_total_duration,
                    current_tc_out=src_tc_out,
                    expected_duration=event.duration_frames,
                    expected_tc_out=event.record_out.timecode,
                )

            with self.subTest(f"Event {i} Record Length"):
                rec_total_duration, rec_tc_out = self.check_running_event(
                    event_in=rec_in,
                    event_out=rec_out,
                    current_total=rec_total_duration,
                    current_tc_out=rec_tc_out,
                    expected_duration=event.duration_frames,
                    expected_tc_out=event.record_out.timecode,
                )
        self.assertEqual(
            rec_total_duration,
            src_total_duration,
            "source and record durations equal",
        )

        self.assertEqual(
            rec_total_duration.frames,
            MANY_BASIC_EDITS_DATA.total_duration_frames,
            "total duration frames expected",
        )

    def check_running_event(
        self,
        event_in: vtc.Timecode,
        event_out: vtc.Timecode,
        current_total: vtc.Timecode,
        current_tc_out: vtc.Timecode,
        expected_duration: int,
        expected_tc_out: str,
    ) -> Tuple[vtc.Timecode, vtc.Timecode]:
        event_len = event_out - event_in
        self.assertEqual(expected_duration, event_len.frames, "duration expected")

        for source in ParseTCCase.Source:
            if source is ParseTCCase.Source.TIMECODE:
                event_len = event_out - event_in.timecode
            elif source is ParseTCCase.Source.FRAC:
                event_len = event_out - event_in.frac
            elif source is ParseTCCase.Source.FRAMES:
                event_len = event_out - event_in.frames
            elif source is ParseTCCase.Source.SECONDS:
                event_len = event_out - event_in.seconds
            elif source is ParseTCCase.Source.FLOAT:
                event_len = event_out - float(event_in.seconds)

            self.assertEqual(
                expected_duration,
                event_len.frames,
                f"duration expected from {source}",
            )

        new_total = current_total + event_len
        new_out = current_tc_out + event_len
        self.assertEqual(expected_tc_out, new_out.timecode, "new tc out expected")

        for source in ParseTCCase.Source:
            if source is ParseTCCase.Source.TIMECODE:
                this_total = current_total + event_len.timecode
                new_out = current_tc_out + event_len.timecode
            elif source is ParseTCCase.Source.FRAC:
                this_total = current_total + event_len.frac
                new_out = current_tc_out + event_len.frac
            elif source is ParseTCCase.Source.FRAMES:
                this_total = current_total + event_len.frames
                new_out = current_tc_out + event_len.frames
            elif source is ParseTCCase.Source.SECONDS:
                this_total = current_total + event_len.seconds
                new_out = current_tc_out + event_len.seconds
            elif source is ParseTCCase.Source.FLOAT:
                this_total = current_total + float(event_len.seconds)
                new_out = current_tc_out + float(event_len.seconds)
            else:
                raise RuntimeError(f"unexpected source: {type(source)}")

            self.assertEqual(
                new_total,
                this_total,
                f"new total expected from {source}",
            )
            self.assertEqual(
                expected_tc_out,
                new_out.timecode,
                f"new tc out expected from {source}",
            )

        return new_total, new_out


class TestTimecodeMethods(unittest.TestCase):
    def test_rebase(self) -> None:
        timecode = vtc.Timecode("01:00:00:00", vtc.RATE.F24)
        rebased = timecode.rebase(vtc.RATE.F48)

        self.assertEqual("00:30:00:00", rebased.timecode, "new tc expected")
        self.assertEqual(timecode.frames, rebased.frames, "frames identical")
