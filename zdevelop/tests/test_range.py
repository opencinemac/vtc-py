import unittest
import vtc

from typing import NamedTuple, List, Optional, Union


class TestRange(unittest.TestCase):
    class BasicCase(NamedTuple):
        tc_in: vtc.Timecode
        tc_out: vtc.Timecode

        length: vtc.Timecode
        contains: List[Union[vtc.TimecodeSource, vtc.Range]]
        not_contains: List[Union[vtc.TimecodeSource, vtc.Range]]

    def test_basic(self) -> None:

        cases: List[TestRange.BasicCase] = [
            TestRange.BasicCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc_out=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                length=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                contains=[
                    "01:00:00:00",
                    "01:30:00:00",
                    "01:59:59:23",
                    vtc.Range(
                        vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:30:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("01:59:59:23", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                ],
                not_contains=[
                    "00:59:59:23",
                    "00:00:00:00",
                    "-01:30:00:00",
                    "02:00:00:00",
                    "03:00:00:00",
                    vtc.Range(
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:01", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("03:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("04:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("00:59:59:23", rate=vtc.RATE.F23_98),
                    ),
                ],
            ),
            TestRange.BasicCase(
                tc_in=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc_out=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                length=vtc.Timecode("00:00:00:01", rate=vtc.RATE.F23_98),
                contains=[
                    "01:00:00:00",
                    vtc.Range(
                        vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                    ),
                ],
                not_contains=[
                    "00:59:59:23",
                    "00:00:00:00",
                    "-01:00:00:00",
                    "02:00:00:00",
                    "03:00:00:00",
                    vtc.Range(
                        vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("02:00:00:01", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("03:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("04:00:00:00", rate=vtc.RATE.F23_98),
                    ),
                    vtc.Range(
                        vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                        vtc.Timecode("00:59:59:23", rate=vtc.RATE.F23_98),
                    ),
                ],
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.tc_in.timecode} - {case.tc_out.timecode}") as t:
                tc_range = vtc.Range(case.tc_in, case.tc_out)
                self.check_range(tc_range, case, "regular")

                tc_range = vtc.Range(case.tc_out, case.tc_in)
                self.check_range(tc_range, case, "flipped")

    def check_range(self, tc_range: vtc.Range, case: BasicCase, test_type: str) -> None:
        self.assertEqual(case.tc_in, tc_range.tc_in, f"{test_type}: tc in expected")
        self.assertEqual(case.tc_out, tc_range.tc_out, f"{test_type}: tc out expected")
        self.assertEqual(case.length, len(tc_range), f"{test_type}: length")

        for contained in case.contains:
            self.assertIn(contained, tc_range, f"{test_type}: contained")

        for not_contained in case.not_contains:
            self.assertNotIn(not_contained, tc_range, f"{test_type}: not contained")

    def test_equality(self) -> None:
        class TestCase(NamedTuple):
            range1: vtc.Range
            range2: vtc.Range
            equal: bool

        cases: List[TestCase] = [
            TestCase(
                range1=vtc.Range(
                    tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                equal=True,
            ),
            TestCase(
                range1=vtc.Range(
                    tc1=vtc.Timecode("01:00:00:01", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                equal=False,
            ),
            TestCase(
                range1=vtc.Range(
                    tc1=vtc.Timecode("03:00:00:01", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("04:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                equal=False,
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.range1} = {case.range2}"):
                self.assertEqual(case.equal, case.range1 == case.range2)

    def test_intersection_separation(self) -> None:
        class TestCase(NamedTuple):
            range1: vtc.Range
            range2: vtc.Range
            intersection: Optional[vtc.Range]
            separation: Optional[vtc.Range]

        cases: List[TestCase] = [
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                separation=None,
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=vtc.Range(
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                separation=None,
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                ),
                separation=None,
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:45:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=vtc.Range(
                    vtc.Timecode("01:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:45:00:00", rate=vtc.RATE.F23_98),
                ),
                separation=None,
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=None,
                separation=vtc.Range(
                    vtc.Timecode("00:30:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                ),
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("00:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("00:59:59:23", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=None,
                separation=vtc.Range(
                    vtc.Timecode("00:59:59:23", rate=vtc.RATE.F23_98),
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                ),
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("03:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=None,
                separation=vtc.Range(
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
            ),
            TestCase(
                range1=vtc.Range(
                    vtc.Timecode("03:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("04:00:00:00", rate=vtc.RATE.F23_98),
                ),
                range2=vtc.Range(
                    vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                ),
                intersection=None,
                separation=vtc.Range(
                    vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
                    vtc.Timecode("3:00:00:00", rate=vtc.RATE.F23_98),
                ),
            ),
        ]

        for case in cases:
            with self.subTest(f"{case.range1} intersects {case.range2}"):
                self.assertEqual(
                    case.intersection,
                    case.range1.intersection(case.range2),
                    f"intersection of {case.range1} and {case.range2}",
                )

                self.assertEqual(
                    case.intersection,
                    case.range2.intersection(case.range1),
                    f"intersection of {case.range2} and {case.range1}",
                )

            with self.subTest(f"{case.range1} separates {case.range2}"):
                self.assertEqual(
                    case.separation,
                    case.range1.separation(case.range2),
                    f"separation of {case.range1} and {case.range2}",
                )

                self.assertEqual(
                    case.separation,
                    case.range2.separation(case.range1),
                    f"separation of {case.range2} and {case.range1}",
                )

    def test_error_mismatched_framerates(self) -> None:
        with self.assertRaises(ValueError) as error:
            vtc.Range(
                tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
                tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F24),
            )

        self.assertEqual(
            "Range in and out must have matching framerate",
            str(error.exception),
        )

    def test_not_equal_to_non_range(self) -> None:
        tc_range = vtc.Range(
            tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
            tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
        )
        self.assertNotEqual(None, tc_range)

    def test_not_contains_non_range(self) -> None:
        tc_range = vtc.Range(
            tc1=vtc.Timecode("01:00:00:00", rate=vtc.RATE.F23_98),
            tc2=vtc.Timecode("02:00:00:00", rate=vtc.RATE.F23_98),
        )
        self.assertNotIn(None, tc_range)
