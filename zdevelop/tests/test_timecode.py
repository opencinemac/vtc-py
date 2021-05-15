import decimal
import enum
import fractions
import vtc
import dataclasses
import unittest
from typing import Tuple, NamedTuple, List, Union, Optional, Any

from zdevelop.tests.conftest import MANY_BASIC_EDITS_DATA, TableTimecodeInfo


@dataclasses.dataclass
class ParseTCCase:
    # The rate these values should be parsed at.
    rate: vtc.Framerate

    # Fractal seconds value to parse / expect.
    frac: fractions.Fraction = fractions.Fraction(0, 1)
    # Fractal int value to parse / expect.
    frames: int = 0
    # The raw frames that came from a reference XML used to test ppro tick correctness
    # with reference data from ppro XML.
    frames_xml_raw: int = 0
    # Premiere Pro ticks expected.
    ppro_ticks: vtc.PremiereTicks = vtc.PremiereTicks(-1)
    # The raw premiere pro ticks from a parsed XML. PPRO ticks are relative to a start
    # value of 0, and not adjusted to account for start tc.
    ppro_ticks_xml_raw: vtc.PremiereTicks = vtc.PremiereTicks(-1)
    # Timecode value to parse / expect.
    timecode: str = ""
    # Decimal seconds value to parse / expect.
    seconds: decimal.Decimal = decimal.Decimal(0)
    # Runtime value to parse / expect.
    runtime: str = ""
    # Feet and frames value to parse / expect
    feet_and_frames: str = ""

    class Source(enum.Enum):

        """
        Source is an enum for signaling what source value we should be parsing from.
        """

        # FRAC means parse from ParseTCCase.frac.
        FRAC = enum.auto()
        # FRAMES means parse from ParseTCCase.frames.
        FRAMES = enum.auto()
        # TIMECODE means parse from ParseTCCase.timecode.
        TIMECODE = enum.auto()
        # SECONDS means parse from ParseTCCase.seconds.
        SECONDS = enum.auto()
        # FLOAT means parse from float(ParseTCCase.seconds).
        FLOAT = enum.auto()
        # RUNTIME means parse from ParseTCCase.runtime.
        RUNTIME = enum.auto()
        # PPRO_TICKS means parse from ParseTCCase.ppro_ticks.
        PPRO_TICKS = enum.auto()
        # FEET_AND_FRAMES means parse from ParseTCCase.feet_and_frames.
        FEET_AND_FRAMES = enum.auto()

    @classmethod
    def from_table_info(cls, event: TableTimecodeInfo) -> "ParseTCCase":
        """from_table_info parses a new ParseTCCase from a TableTimecodeInfo."""
        return cls(
            rate=vtc.Framerate(
                event.frame_rate_frac,
                ntsc=event.ntsc,
                dropframe=event.drop_frame,
            ),
            frac=event.seconds_rational,
            frames=event.frame,
            frames_xml_raw=event.frame_xml_raw,
            ppro_ticks=event.ppro_ticks,
            ppro_ticks_xml_raw=event.ppro_ticks_xml_raw,
            timecode=event.timecode,
            seconds=event.seconds_decimal,
            feet_and_frames=event.feet_and_frames,
            runtime=event.runtime,
        )


class TestParse(unittest.TestCase):

    """Tests parsing timecodes."""

    def test_parse_timecode(self) -> None:
        """Test parsing and rendering a set of hand-written timecode representations."""
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
                feet_and_frames="5400+00",
                ppro_ticks=vtc.PremiereTicks(915372057600000),
            ),
            # Test Negative
            ParseTCCase(
                rate=vtc.RATE.F23_98,
                frac=-fractions.Fraction(18018, 5),
                frames=-86400,
                timecode="-01:00:00:00",
                seconds=-decimal.Decimal("3603.6"),
                runtime="-01:00:03.6",
                feet_and_frames="-5400+00",
                ppro_ticks=vtc.PremiereTicks(-915372057600000),
            ),
            ParseTCCase(
                rate=vtc.RATE.F23_98,
                frac=fractions.Fraction(12012, 5),
                frames=57600,
                timecode="00:40:00:00",
                seconds=decimal.Decimal("2402.4"),
                runtime="00:40:02.4",
                feet_and_frames="3600+00",
                ppro_ticks=vtc.PremiereTicks(610248038400000),
            ),
            # Test negative
            ParseTCCase(
                rate=vtc.RATE.F23_98,
                frac=-fractions.Fraction(12012, 5),
                frames=-57600,
                timecode="-00:40:00:00",
                seconds=-decimal.Decimal("2402.4"),
                runtime="-00:40:02.4",
                feet_and_frames="-3600+00",
                ppro_ticks=vtc.PremiereTicks(-610248038400000),
            ),
            # 24 ---------------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=fractions.Fraction(3600, 1),
                frames=86400,
                timecode="01:00:00:00",
                seconds=decimal.Decimal(3600),
                runtime="01:00:00.0",
                feet_and_frames="5400+00",
                ppro_ticks=vtc.PremiereTicks(914457600000000),
            ),
            # Negative
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=-fractions.Fraction(3600, 1),
                frames=-86400,
                timecode="-01:00:00:00",
                seconds=-decimal.Decimal(3600),
                runtime="-01:00:00.0",
                feet_and_frames="-5400+00",
                ppro_ticks=vtc.PremiereTicks(-914457600000000),
            ),
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=fractions.Fraction(2400, 1),
                frames=57600,
                timecode="00:40:00:00",
                seconds=decimal.Decimal("2400.0"),
                runtime="00:40:00.0",
                feet_and_frames="3600+00",
                ppro_ticks=vtc.PremiereTicks(609638400000000),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F24,
                frac=-fractions.Fraction(2400, 1),
                frames=-57600,
                timecode="-00:40:00:00",
                seconds=-decimal.Decimal("2400.0"),
                runtime="-00:40:00.0",
                feet_and_frames="-3600+00",
                ppro_ticks=vtc.PremiereTicks(-609638400000000),
            ),
            # 29.97 DF ---------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(0, 1),
                frames=0,
                timecode="00:00:00;00",
                seconds=decimal.Decimal("0.0"),
                runtime="00:00:00.0",
                feet_and_frames="0+00",
                ppro_ticks=vtc.PremiereTicks(0),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(31031, 15000),
                frames=62,
                timecode="00:00:02;02",
                seconds=decimal.Decimal("2.068733333333333333333333333"),
                runtime="00:00:02.068733333",
                feet_and_frames="3+14",
                ppro_ticks=vtc.PremiereTicks(525491366400),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(31031, 15000),
                frames=-62,
                timecode="-00:00:02;02",
                seconds=-decimal.Decimal("2.068733333333333333333333333"),
                runtime="-00:00:02.068733333",
                feet_and_frames="-3+14",
                ppro_ticks=vtc.PremiereTicks(-525491366400),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(3003, 50),
                frames=1800,
                timecode="00:01:00;02",
                seconds=decimal.Decimal("60.06"),
                runtime="00:01:00.06",
                feet_and_frames="112+08",
                ppro_ticks=vtc.PremiereTicks(15256200960000),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(3003, 50),
                frames=-1800,
                timecode="-00:01:00;02",
                seconds=-decimal.Decimal("60.06"),
                runtime="-00:01:00.06",
                feet_and_frames="-112+08",
                ppro_ticks=vtc.PremiereTicks(-15256200960000),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(1800799, 15000),
                frames=3598,
                timecode="00:02:00;02",
                seconds=decimal.Decimal("120.0532666666666666666666667"),
                runtime="00:02:00.053266667",
                feet_and_frames="224+14",
                ppro_ticks=vtc.PremiereTicks(30495450585600),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(1800799, 15000),
                frames=-3598,
                timecode="-00:02:00;02",
                seconds=-decimal.Decimal("120.0532666666666666666666667"),
                runtime="-00:02:00.053266667",
                feet_and_frames="-224+14",
                ppro_ticks=vtc.PremiereTicks(-30495450585600),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(2999997, 5000),
                frames=17982,
                timecode="00:10:00;00",
                seconds=decimal.Decimal("599.9994"),
                runtime="00:09:59.9994",
                feet_and_frames="1123+14",
                ppro_ticks=vtc.PremiereTicks(152409447590400),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(2999997, 5000),
                frames=-17982,
                timecode="-00:10:00;00",
                seconds=-decimal.Decimal("599.9994"),
                runtime="-00:09:59.9994",
                feet_and_frames="-1123+14",
                ppro_ticks=vtc.PremiereTicks(-152409447590400),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(3300297, 5000),
                frames=19782,
                timecode="00:11:00;02",
                seconds=decimal.Decimal("660.0594"),
                runtime="00:11:00.0594",
                feet_and_frames="1236+06",
                ppro_ticks=vtc.PremiereTicks(167665648550400),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(3300297, 5000),
                frames=-19782,
                timecode="-00:11:00;02",
                seconds=-decimal.Decimal("660.0594"),
                runtime="-00:11:00.0594",
                feet_and_frames="-1236+06",
                ppro_ticks=vtc.PremiereTicks(-167665648550400),
            ),
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=fractions.Fraction(8999991, 2500),
                frames=107892,
                timecode="01:00:00;00",
                seconds=decimal.Decimal("3599.9964"),
                runtime="00:59:59.9964",
                feet_and_frames="6743+04",
                ppro_ticks=vtc.PremiereTicks(914456685542400),
            ),
            # negative
            ParseTCCase(
                rate=vtc.RATE.F29_97_DF,
                frac=-fractions.Fraction(8999991, 2500),
                frames=-107892,
                timecode="-01:00:00;00",
                seconds=-decimal.Decimal("3599.9964"),
                runtime="-00:59:59.9964",
                feet_and_frames="-6743+04",
                ppro_ticks=vtc.PremiereTicks(-914456685542400),
            ),
            # 59.94 DF ---------------------------
            # ------------------------------------
            ParseTCCase(
                rate=vtc.RATE.F59_94_DF,
                frac=fractions.Fraction(0, 1),
                frames=0,
                timecode="00:00:00;00",
                seconds=decimal.Decimal("0.0"),
                runtime="00:00:00.0",
                feet_and_frames="0+00",
                ppro_ticks=vtc.PremiereTicks(0),
            ),
            ParseTCCase(
                rate=vtc.RATE.F59_94_DF,
                frac=fractions.Fraction(61061, 60000),
                frames=61,
                timecode="00:00:01;01",
                    seconds=decimal.Decimal("1.017683333333333333333333333"),
                runtime="00:00:01.017683333",
                feet_and_frames="3+13",
                ppro_ticks=vtc.PremiereTicks(258507849600),
            ),
            ParseTCCase(
                rate=vtc.RATE.F59_94_DF,
                frac=fractions.Fraction(21021, 20000),
                frames=63,
                timecode="00:00:01;03",
                seconds=decimal.Decimal("1.05105"),
                runtime="00:00:01.05105",
                feet_and_frames="3+15",
                ppro_ticks=vtc.PremiereTicks(266983516800),
            ),
            # This is the first minute we should be skipping frames on. For 59.94 we
            # skip 4 frames.
            ParseTCCase(
                rate=vtc.RATE.F59_94_DF,
                frac=fractions.Fraction(3003, 50),
                frames=3600,
                timecode="00:01:00;04",
                seconds=decimal.Decimal("60.06"),
                runtime="00:01:00.06",
                feet_and_frames="225+00",
                ppro_ticks=vtc.PremiereTicks(15256200960000),
            ),
        ]

        for case in cases:
            self._run_parse_case(case)

    def test_parse_overflows(self) -> None:
        """Tests that we parse timecodes with overflowed positions correctly."""

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
            TestCase(
                "123:00:00:00",
                "123:00:00:00",
            ),
            TestCase(
                "01:00:00:48",
                "01:00:02:00",
            ),
            TestCase(
                "01:00:120:00",
                "01:02:00:00",
            ),
            TestCase(
                "01:120:00:00",
                "03:00:00:00",
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.str_in} -> {case.str_out}"):
                tc = vtc.Timecode(case.str_in, rate=vtc.RATE.F24)
                self.assertEqual(case.str_out, tc.timecode)

    def test_partial_timecodes(self) -> None:
        """Test that we can parse timecodes missing sections."""

        class TestCase(NamedTuple):
            str_in: str
            str_out: str

        cases: List[TestCase] = [
            TestCase(
                "1:02:03:04",
                "01:02:03:04",
            ),
            TestCase(
                "02:03:04",
                "00:02:03:04",
            ),
            TestCase(
                "2:03:04",
                "00:02:03:04",
            ),
            TestCase(
                "03:04",
                "00:00:03:04",
            ),
            TestCase(
                "3:04",
                "00:00:03:04",
            ),
            TestCase(
                "04",
                "00:00:00:04",
            ),
            TestCase(
                "4",
                "00:00:00:04",
            ),
            TestCase(
                "1:2:3:4",
                "01:02:03:04",
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.str_in} -> {case.str_out}"):
                tc = vtc.Timecode(case.str_in, rate=vtc.RATE.F24)
                self.assertEqual(case.str_out, tc.timecode)

    def test_partial_runtime(self) -> None:
        """Test that we can parse runtimes missing sections."""

        class TestCase(NamedTuple):
            str_in: str
            str_out: str

        cases: List[TestCase] = [
            TestCase(
                "1:02:03.5",
                "01:02:03:12",
            ),
            TestCase(
                "02:03.5",
                "00:02:03:12",
            ),
            TestCase(
                "2:03.5",
                "00:02:03:12",
            ),
            TestCase(
                "03.5",
                "00:00:03:12",
            ),
            TestCase(
                "3.5",
                "00:00:03:12",
            ),
            TestCase(
                "0.5",
                "00:00:00:12",
            ),
            TestCase(
                "1:2:3.5",
                "01:02:03:12",
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.str_in} -> {case.str_out}"):
                tc = vtc.Timecode(case.str_in, rate=vtc.RATE.F24)
                self.assertEqual(case.str_out, tc.timecode)

    def test_parse_from_other(self) -> None:
        """Tests instantiating one Timecode value from another."""
        tc1 = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98)
        tc2 = vtc.Timecode(tc1, rate=None)

        self.assertEqual(tc1, tc2)

    def test_error_parse_unsupported_type(self) -> None:
        """Tests error for trying to parse an unsupported type."""
        with self.assertRaises(TypeError) as caught:
            vtc.Timecode(dict(), rate=vtc.RATE.F24)  # type: ignore

        self.assertEqual(
            "unsupported type for Timecode conversion: <class 'dict'>",
            str(caught.exception),
        )

    def test_error_parse_bad_string(self) -> None:
        """Tests error for attempting to parse an unknown string pattern."""
        with self.assertRaises(ValueError) as caught:
            vtc.Timecode("notatimecode", rate=vtc.RATE.F24)  # type: ignore

        self.assertEqual(
            "'notatimecode' is not a recognized timecode format",
            str(caught.exception),
        )

    def test_error_invalid_drop_frame_value_2997(self) -> None:
        """Tests error for trying to parse an invalid drop-frame value."""
        for i in range(0, 2):
            with self.subTest(f"frames: {i}"):
                with self.assertRaises(ValueError) as caught:
                    vtc.Timecode(  # type: ignore
                        f"00:01:00:0{i}",
                        rate=vtc.RATE.F29_97_DF,
                    )

                self.assertEqual(
                    "drop-frame tc cannot have a frames value of less than 2 on minutes"
                    f" not divisible by 10, found '{i}'",
                    str(caught.exception),
                )

    def test_error_invalid_drop_frame_value_5994(self) -> None:
        for i in range(0, 4):
            with self.subTest(f"frames: {i}"):
                with self.assertRaises(ValueError) as caught:
                    vtc.Timecode(  # type: ignore
                        f"00:01:00:0{i}",
                        rate=vtc.RATE.F59_94_DF,
                    )

                self.assertEqual(
                    "drop-frame tc cannot have a frames value of less than 4 on minutes"
                    f" not divisible by 10, found '{i}'",
                    str(caught.exception),
                )

    def test_error_on_class_with_rate(self) -> None:
        """Tests that we get an error when supplying a vtc.Timecode and rate."""
        with self.assertRaises(ValueError) as caught:
            tc = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98)
            vtc.Timecode(tc, rate=vtc.RATE.F23_98)

        self.assertEqual(
            "rate must be None if src is vtc.Timecode. To rebase Timecode, use"
            "vtc.Timecode.rebase",
            str(caught.exception),
            "error message",
        )

    def test_error_none_framerate(self) -> None:
        """Tests that we get an error when no framerate can be found."""
        with self.assertRaises(ValueError) as caught:
            vtc.Timecode("01:00:00:00", rate=None)

        self.assertEqual(
            "rate must be set for all Timecode src types except vtc.Timecode",
            str(caught.exception),
            "error message",
        )

    def test_parse_timeline_tc(self) -> None:
        """
        Tests parsing a series of timecode events from real CMX3600 and FCP7XML
        cutlists.

        This should increase the confidence that our parsers are working correctly.
        """
        for i, event in enumerate(MANY_BASIC_EDITS_DATA.events):
            rec_in = ParseTCCase.from_table_info(event.record_in)
            self._run_parse_case(rec_in, name=f"EVENT {str(i).zfill(3)} REC IN")

            rec_out = ParseTCCase.from_table_info(event.record_out)
            self._run_parse_case(rec_out, name=f"EVENT {str(i).zfill(3)} REC OUT")

            src_in = ParseTCCase.from_table_info(event.source_in)
            self._run_parse_case(src_in, name=f"EVENT {str(i).zfill(3)} SRC IN")

            src_out = ParseTCCase.from_table_info(event.source_out)
            self._run_parse_case(src_out, name=f"EVENT {str(i).zfill(3)} SRC OUT")

    def _run_parse_case(self, case: ParseTCCase, name: str = "") -> None:
        """Runs a test case for test_parse_timeline_tc or test_parse_timecode."""
        for source in ParseTCCase.Source:
            sub_name = ""
            if name != "":
                sub_name = name + ": "
            sub_name += f"{repr(case.timecode)} FROM: {source.name} @ {case.rate}"

            with self.subTest(sub_name):
                if source is ParseTCCase.Source.FRAC:
                    tc = vtc.Timecode(case.frac, rate=case.rate)
                elif source is ParseTCCase.Source.TIMECODE:
                    tc = vtc.Timecode(case.timecode, rate=case.rate)
                elif source is ParseTCCase.Source.FRAMES:
                    tc = vtc.Timecode(case.frames, rate=case.rate)
                elif source is ParseTCCase.Source.SECONDS:
                    tc = vtc.Timecode(case.seconds, rate=case.rate)
                elif source is ParseTCCase.Source.FLOAT:
                    tc = vtc.Timecode(float(case.seconds), rate=case.rate)
                elif source is ParseTCCase.Source.RUNTIME:
                    tc = vtc.Timecode(case.runtime, rate=case.rate)
                elif source is ParseTCCase.Source.PPRO_TICKS:
                    if case.ppro_ticks == -1:
                        continue
                    tc = vtc.Timecode(case.ppro_ticks, rate=case.rate)
                elif source is ParseTCCase.Source.FEET_AND_FRAMES:
                    tc = vtc.Timecode(case.feet_and_frames, rate=case.rate)
                else:
                    raise RuntimeError("source not known for test case")

                self.assertEqual(
                    case.timecode,
                    tc.timecode,
                    msg=f"parsed timecode expected with rate {repr(tc.rate)}",
                )
                self.assertEqual(case.frac, tc.rational, "parsed rational expected")
                self.assertEqual(
                    case.frames,
                    tc.frames,
                    msg="parsed frames expected",
                )
                if case.ppro_ticks != -1:
                    self.assertEqual(
                        case.ppro_ticks,
                        tc.premiere_ticks,
                        msg="parsed ppro ticks expected",
                    )
                self.assertEqual(
                    case.seconds,
                    tc.seconds,
                    msg="parsed seconds expected",
                )
                self.assertEqual(
                    case.feet_and_frames,
                    tc.feet_and_frames,
                    msg="feet and frames expected",
                )
                self.assertEqual(
                    case.runtime,
                    tc.runtime(),
                    msg="parsed runtime expected",
                )

        if case.ppro_ticks_xml_raw != -1 and case.frames_xml_raw != -1:
            with self.subTest(name + " XML Ticks Match Frames"):
                # The ppro ticks in the source XML is based on the frame number starting
                # at 0, not the timecode start time. We are going to re-parse a new
                # tc from the raw xml frame count, and see if it's ppro_ticks matches
                # what was in the xml.
                if case.ppro_ticks != -1:
                    self.assertEqual(
                        case.ppro_ticks_xml_raw,
                        vtc.Timecode(
                            case.frames_xml_raw,
                            rate=case.rate,
                        ).premiere_ticks,
                        (
                            f"raw premiere ticks expected from frames: "
                            f"{case.frames_xml_raw}",
                        ),
                    )


class TestMagicMethods(unittest.TestCase):

    """TestMagicMethods tests our Timecode's dunder methods like __add__ and __lt__."""

    def test_compare(self) -> None:
        """
        test_compare tests the comparison methods:
            __eq__
            __lt__
            __gt__
            __lte__
            __gte__
        """

        class TestCase(NamedTuple):
            """
            Each test case will check ALL comparison methods using known eq an lt
            expectations.
            """

            tc1: vtc.Timecode
            tc2: vtc.TimecodeSource
            eq: bool
            lt: bool

        cases: List[TestCase] = [
            # 24 FPS ----------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=vtc.Timecode("00:59:59:24", rate=vtc.RATE.F24),
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F24),
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F24),
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=vtc.Timecode("00:59:59:23", rate=vtc.RATE.F24),
                eq=False,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=86400,
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=86399,
                eq=False,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=fractions.Fraction(3600, 1),
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=3600.0,
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=decimal.Decimal("3600.0"),
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                tc2=fractions.Fraction(3600, 1),
                eq=True,
                lt=False,
            ),
            # 23.98 --------------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=decimal.Decimal("3603.6"),
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=3603.6,
                eq=True,
                lt=False,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=86401,
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode(86401, rate=vtc.RATE.F23_98),
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                eq=False,
                lt=True,
            ),
            TestCase(
                tc1=vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                eq=False,
                lt=True,
            ),
            # Mixed ---------------------------------------------
            TestCase(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                eq=False,
                lt=False,
            ),
        ]

        for case in cases:
            # For each case we are going to flip the values and expectations to make
            # sure comparisons between different types work in both directions.

            # __eq__
            test_name = f"{repr(case.tc1)} == {repr(case.tc2)} is {case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.eq, case.tc1 == case.tc2, test_name)

            # __eq__ flipped
            test_name = f"{repr(case.tc2)} == {repr(case.tc1)} is {case.eq}"
            with self.subTest(test_name):
                self.assertEqual(case.eq, case.tc2 == case.tc1, test_name)

            # __lt__
            test_name = f"{repr(case.tc1)} < {repr(case.tc2)} is {case.lt}"
            with self.subTest(test_name):
                self.assertEqual(case.lt, case.tc1 < case.tc2, test_name)

            # __lt__ flipped
            expected_lt = not case.lt and not case.eq
            test_name = f"{repr(case.tc2)} < {repr(case.tc1)} is {expected_lt}"
            with self.subTest(test_name):
                self.assertEqual(
                    expected_lt,
                    case.tc2 < case.tc1,
                    test_name,
                )

            # __lte__
            expected_lte = case.lt or case.eq
            test_name = f"{repr(case.tc1)} <= {repr(case.tc2)} is {expected_lte}"
            with self.subTest(test_name):
                self.assertEqual(expected_lte, case.tc1 <= case.tc2, test_name)

            # __lte__ flipped
            expected_lte = not case.lt or case.eq
            test_name = f"{repr(case.tc2)} <= {repr(case.tc1)} is {expected_lte}"
            with self.subTest(test_name):
                self.assertEqual(not case.lt or case.eq, case.tc2 <= case.tc1)

            # __gt__
            expected_gt = not case.eq and not case.lt
            test_name = f"{repr(case.tc1)} > {repr(case.tc2)} is {expected_gt}"
            with self.subTest(test_name):
                self.assertEqual(expected_gt, case.tc1 > case.tc2, test_name)

            # __gt__ flipped
            expected_gt = case.lt
            test_name = f"{repr(case.tc1)} > {repr(case.tc2)} is {expected_gt}"
            with self.subTest(test_name):
                self.assertEqual(
                    expected_gt,
                    case.tc2 > case.tc1,
                    test_name,
                )

            # __gte__
            expected_gte = case.eq or not case.lt
            test_name = f"{repr(case.tc1)} >= {repr(case.tc2)} is {expected_gte}"
            with self.subTest(test_name):
                self.assertEqual(expected_gte, case.tc1 >= case.tc2, test_name)

            # __gte__ flipped
            expected_gte = case.eq or case.lt
            test_name = f"{repr(case.tc2)} > {repr(case.tc1)} is {expected_gte}"
            with self.subTest(test_name):
                self.assertEqual(
                    expected_gte,
                    case.tc2 >= case.tc1,
                    test_name,
                )

    def test_compare_not_implemented(self) -> None:
        """
        Tests that false is returned when comparison is not implemented by __eq__ for
        other type.
        """
        self.assertNotEqual(
            vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
            dict(),
            "unsupported type not equal",
        )

    def test_sort_timecodes(self) -> None:
        """Test that timecodes are sorted correctly through comparison operators."""

        class TestCase(NamedTuple):
            tcs_in: List[vtc.Timecode]
            tcs_out: List[vtc.Timecode]

        cases: List[TestCase] = [
            TestCase(
                tcs_in=[
                    vtc.Timecode("00:01:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("00:00:10:00", rate=vtc.RATE.F23_98),
                ],
                tcs_out=[
                    vtc.Timecode("00:00:10:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("00:01:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                ],
            )
        ]

        for i, case in enumerate(cases):
            with self.subTest(i):
                sorted_timecodes = sorted(case.tcs_in)
                self.assertListEqual(case.tcs_out, sorted_timecodes, "sorted correctly")

    def test_multiply(self) -> None:
        """Test __mul__."""

        class TestCase(NamedTuple):
            tc_in: vtc.Timecode
            multiplier: Union[int, float, decimal.Decimal, fractions.Fraction]
            expected: vtc.Timecode

        cases: List[TestCase] = [
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                multiplier=2,
                expected=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                multiplier=2,
                expected=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                multiplier=1.5,
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                multiplier=1.5,
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                multiplier=fractions.Fraction(3, 2),
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                multiplier=fractions.Fraction(3, 2),
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                multiplier=decimal.Decimal("1.5"),
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                multiplier=decimal.Decimal("1.5"),
                expected=vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                multiplier=0.5,
                expected=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                multiplier=0.5,
                expected=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
            ),
        ]

        for case in cases:
            name = f"{case.tc_in} * {case.multiplier} = {case.expected}"
            with self.subTest(name):
                result = case.tc_in * case.multiplier
                self.assertEqual(case.expected, result, name)

    def test_divmod(self) -> None:
        """Test __divmod__, __floordiv__ and __mod__."""

        class TestCase(NamedTuple):
            source: vtc.Timecode
            divisor: Union[int, float, decimal.Decimal, fractions.Fraction]
            expected_dividend: vtc.Timecode
            expected_modulo: vtc.Timecode
            expected_truediv: Optional[vtc.Timecode] = None

        cases: List[TestCase] = [
            TestCase(
                source=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:00", rate=vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F24),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                divisor=2,
                expected_dividend=vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F24),
                divisor=4,
                expected_dividend=vtc.Timecode("00:15:00:00", rate=vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                divisor=4,
                expected_dividend=vtc.Timecode("00:15:00:00", rate=vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F23_98),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F24),
                divisor=1.5,
                expected_dividend=vtc.Timecode("00:40:00:00", rate=vtc.RATE.F24),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F24),
                expected_truediv=vtc.Timecode("00:40:00:01", rate=vtc.RATE.F24),
            ),
            TestCase(
                source=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                divisor=1.5,
                expected_dividend=vtc.Timecode("00:40:00:00", rate=vtc.RATE.F23_98),
                expected_modulo=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F23_98),
                expected_truediv=vtc.Timecode("00:40:00:01", rate=vtc.RATE.F23_98),
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

    def test_neg(self) -> None:
        """Tests __neg__."""
        tc = vtc.Timecode("01:00:04:14", rate=vtc.RATE.F24)
        neg = -tc

        self.assertEqual("-01:00:04:14", neg.timecode, "timecode is negative")
        self.assertEqual(-tc.rational, neg.rational, "fraction is negative")

    def test_abs(self) -> None:
        """Tests __abs__."""

        class TestCase(NamedTuple):
            tc_in: vtc.Timecode
            abs: vtc.Timecode

        cases: List[TestCase] = [
            TestCase(
                tc_in=vtc.Timecode("-01:00:04:14", rate=vtc.RATE.F24),
                abs=vtc.Timecode("01:00:04:14", rate=vtc.RATE.F24),
            ),
            TestCase(
                tc_in=vtc.Timecode("01:00:04:14", rate=vtc.RATE.F24),
                abs=vtc.Timecode("01:00:04:14", rate=vtc.RATE.F24),
            ),
        ]

        for case in cases:
            test_name = f"abs({case.tc_in}) = {case.abs}"
            with self.subTest(test_name):
                abs_tc = abs(case.tc_in)

                self.assertGreater(abs_tc.rational, 0, "value is greater than zero")
                self.assertEqual(
                    case.abs.timecode,
                    abs_tc.timecode,
                    "timecode is expected",
                )
                self.assertEqual(case.abs.rational, abs_tc.rational, "frac is expected")

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
            dropframe=MANY_BASIC_EDITS_DATA.start_time.drop_frame,
        )

        rec_total_duration = vtc.Timecode(0, rate=seq_framerate)
        rec_tc_out = vtc.Timecode(
            MANY_BASIC_EDITS_DATA.events[0].record_in.timecode,
            rate=seq_framerate,
        )

        src_total_duration = rec_total_duration
        src_tc_out = vtc.Timecode(
            MANY_BASIC_EDITS_DATA.events[0].record_in.timecode,
            rate=seq_framerate,
        )

        for i, event in enumerate(MANY_BASIC_EDITS_DATA.events):
            with self.subTest(f"Event {i} Parse"):
                rec_in_info = ParseTCCase.from_table_info(event.record_in)
                rec_in = vtc.Timecode(rec_in_info.timecode, rate=rec_in_info.rate)

                rec_out_info = ParseTCCase.from_table_info(event.record_out)
                rec_out = vtc.Timecode(rec_out_info.timecode, rate=rec_out_info.rate)

                src_in_info = ParseTCCase.from_table_info(event.source_in)
                src_in = vtc.Timecode(src_in_info.timecode, rate=src_in_info.rate)

                src_out_info = ParseTCCase.from_table_info(event.source_out)
                src_out = vtc.Timecode(src_out_info.timecode, rate=src_out_info.rate)

            with self.subTest(f"Event {i} Source Length"):
                src_total_duration, src_tc_out = self._check_running_event(
                    event_in=src_in,
                    event_out=src_out,
                    current_total=src_total_duration,
                    current_tc_out=src_tc_out,
                    expected_duration=event.duration_frames,
                    expected_tc_out=event.record_out.timecode,
                )

            with self.subTest(f"Event {i} Record Length"):
                rec_total_duration, rec_tc_out = self._check_running_event(
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

    def _check_running_event(
        self,
        event_in: vtc.Timecode,
        event_out: vtc.Timecode,
        current_total: vtc.Timecode,
        current_tc_out: vtc.Timecode,
        expected_duration: int,
        expected_tc_out: str,
    ) -> Tuple[vtc.Timecode, vtc.Timecode]:
        """
        _check_running_event checks that adding the next event to our running totals
        results in the expected new total value.
        """
        event_len = event_out - event_in
        self.assertEqual(expected_duration, event_len.frames, "duration expected")

        for source in ParseTCCase.Source:
            source_value: Any

            source_value, event_len = self._check_running_events_get_event_length(
                source,
                event_in,
                event_out,
            )

            self.assertEqual(
                expected_duration,
                event_len.frames,
                f"duration expected from {source} value: {repr(source_value)}",
            )

        new_total = current_total + event_len
        new_out = current_tc_out + event_len
        self.assertEqual(expected_tc_out, new_out.timecode, "new tc out expected")

        for source in ParseTCCase.Source:
            this_total, new_out = self._check_running_events_get_length_total(
                source,
                current_total,
                current_tc_out,
                event_len,
            )

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

    @staticmethod
    def _check_running_events_get_event_length(
        source: ParseTCCase.Source,
        event_in: vtc.Timecode,
        event_out: vtc.Timecode,
    ) -> Tuple[vtc.TimecodeSource, vtc.Timecode]:
        """
        _check_running_events_get_length gets the event length by subtracting the source
        type from event_in. It also returns the source value used for logging.
        """
        source_value: vtc.TimecodeSource

        if source is ParseTCCase.Source.TIMECODE:
            source_value = event_in.timecode
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.FRAC:
            source_value = event_in.rational
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.FRAMES:
            source_value = event_in.frames
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.SECONDS:
            source_value = event_in.seconds
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.FLOAT:
            source_value = float(event_in.seconds)
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.RUNTIME:
            source_value = event_in.runtime()
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.PPRO_TICKS:
            source_value = event_in.premiere_ticks
            event_len = event_out - source_value
        elif source is ParseTCCase.Source.FEET_AND_FRAMES:
            source_value = event_in.feet_and_frames
            event_len = event_out - source_value
        else:
            raise RuntimeError("unknown source type:", source.name)

        return source_value, event_len

    @staticmethod
    def _check_running_events_get_length_total(
        source: ParseTCCase.Source,
        current_total: vtc.Timecode,
        current_tc_out: vtc.Timecode,
        event_len: vtc.Timecode,
    ) -> Tuple[vtc.Timecode, vtc.Timecode]:
        """
        _check_running_events_get_length_total gets our new running totals by adding
        the source type of event_len to current_total and current_tc_out.
        """
        if source is ParseTCCase.Source.TIMECODE:
            this_total = current_total + event_len.timecode
            new_out = current_tc_out + event_len.timecode
        elif source is ParseTCCase.Source.FRAC:
            this_total = current_total + event_len.rational
            new_out = current_tc_out + event_len.rational
        elif source is ParseTCCase.Source.FRAMES:
            this_total = current_total + event_len.frames
            new_out = current_tc_out + event_len.frames
        elif source is ParseTCCase.Source.SECONDS:
            this_total = current_total + event_len.seconds
            new_out = current_tc_out + event_len.seconds
        elif source is ParseTCCase.Source.FLOAT:
            this_total = current_total + float(event_len.seconds)
            new_out = current_tc_out + float(event_len.seconds)
        elif source is ParseTCCase.Source.RUNTIME:
            this_total = current_total + event_len.runtime()
            new_out = current_tc_out + event_len.runtime()
        elif source is ParseTCCase.Source.PPRO_TICKS:
            this_total = current_total + event_len.premiere_ticks
            new_out = current_tc_out + event_len.premiere_ticks
        elif source is ParseTCCase.Source.FEET_AND_FRAMES:
            this_total = current_total + event_len.feet_and_frames
            new_out = current_tc_out + event_len.feet_and_frames
        else:
            raise RuntimeError(f"unexpected source: {source.name}")

        return this_total, new_out


class TestTimecodeMethods(unittest.TestCase):

    """TestTimecodeMethods tests non value representon or magic timecode methods."""

    def test_rebase(self) -> None:
        """test_rebase tests rebasing a timecode in another framerate."""
        timecode = vtc.Timecode("01:00:00:00", rate=vtc.RATE.F24)
        rebased = timecode.rebase(vtc.RATE.F48)

        self.assertEqual("00:30:00:00", rebased.timecode, "new tc expected")
        self.assertEqual(timecode.frames, rebased.frames, "frames identical")
