import dataclasses
import decimal
import fractions
import json
import pathlib

from typing import Dict, Any, List

import vtc


@dataclasses.dataclass(frozen=True)
class TableTimecodeInfo:
    timebase: int
    ntsc: bool
    drop_frame: bool
    frame_rate_frac: fractions.Fraction
    timecode: str
    frame: int
    frame_xml_raw: int
    ppro_ticks: vtc.PremiereTicks
    ppro_ticks_xml_raw: vtc.PremiereTicks
    seconds_rational: fractions.Fraction
    seconds_decimal: decimal.Decimal
    feet_and_frames: str
    runtime: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "TableTimecodeInfo":
        # Make a shallow copy of the dict.
        data = {k: v for k, v in data.items()}

        # Replace values we need to convert
        data["frame_rate_frac"] = fractions.Fraction(data["frame_rate_frac"])
        data["seconds_rational"] = fractions.Fraction(data["seconds_rational"])
        data["seconds_decimal"] = decimal.Decimal(data["seconds_decimal"])
        data["ppro_ticks"] = vtc.PremiereTicks(data["ppro_ticks"])
        data["ppro_ticks_xml_raw"] = vtc.PremiereTicks(data["ppro_ticks_xml_raw"])

        # Pass the dict in as a kwargs object.
        return TableTimecodeInfo(**data)


@dataclasses.dataclass(frozen=True)
class TableEventInfo:
    duration_frames: int
    source_in: TableTimecodeInfo
    source_out: TableTimecodeInfo
    record_in: TableTimecodeInfo
    record_out: TableTimecodeInfo

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "TableEventInfo":
        data = {k: v for k, v in data.items()}
        data["source_in"] = TableTimecodeInfo.from_json(data["source_in"])
        data["source_out"] = TableTimecodeInfo.from_json(data["source_out"])
        data["record_in"] = TableTimecodeInfo.from_json(data["record_in"])
        data["record_out"] = TableTimecodeInfo.from_json(data["record_out"])

        return TableEventInfo(**data)


@dataclasses.dataclass(frozen=True)
class TableSequenceInfo:
    start_time: TableTimecodeInfo
    total_duration_frames: int
    events: List[TableEventInfo]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "TableSequenceInfo":
        data = {k: v for k, v in data.items()}
        data["start_time"] = TableTimecodeInfo.from_json(data["start_time"])

        events = list()
        for event_data in data["events"]:
            event = TableEventInfo.from_json(event_data)
            events.append(event)

        data["events"] = events

        return TableSequenceInfo(**data)


def _load_timeline_table_data(path: pathlib.Path) -> TableSequenceInfo:
    path = pathlib.Path(__file__).absolute().parent / "test-timelines" / path

    with path.open("r") as f:
        data = json.load(f)

    return TableSequenceInfo.from_json(data)


MANY_BASIC_EDITS_DATA: TableSequenceInfo = _load_timeline_table_data(
    pathlib.Path("PPRO/Many Basic Edits/Many Basic Edits.json"),
)
