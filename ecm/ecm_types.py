# class EcmLogLine()

from ecm.RE_VERSION import (
    RE_COMPOSITE_FACTOR,
    RE_FACTOR_FOUND,
    RE_INPUT,
    RE_PRIME_COFACTOR,
    RE_RUN,
    RE_STEP,
    RE_USING,
    RE_VERSION,
)


from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class EcmStatus:

    start_time: Optional[datetime] = None
    version: Optional[str] = None

    input_number: Optional[str] = None
    input_digits: Optional[int] = None

    run_current: Optional[int] = None
    run_total: Optional[int] = None

    B1: Optional[int] = None
    B2: Optional[int] = None
    polynomial: Optional[str] = None
    sigma: Optional[str] = None

    latest_step: Optional[int] = None
    latest_step_ms: Optional[int] = None

    factor_found: Optional[str] = None
    factor_step: Optional[int] = None

    composite_factors: List[str] = []
    prime_cofactors: List[str] = []

    def _parse_line(self, line: str):
        if m := RE_VERSION.search(line):
            self.status_data.version = m.group("version")
            return

        if m := RE_INPUT.search(line):
            self.status_data.input_number = m.group("number")
            self.status_data.input_digits = int(m.group("digits"))
            return

        if m := RE_RUN.search(line):
            self.status_data.run_current = int(m.group("current"))
            self.status_data.run_total = int(m.group("total"))
            return

        if m := RE_USING.search(line):
            self.status_data.B1 = int(m.group("B1"))
            self.status_data.B2 = int(m.group("B2"))
            self.status_data.polynomial = m.group("polynomial")
            self.status_data.sigma = m.group("sigma")
            return

        if m := RE_STEP.search(line):
            self.status_data.latest_step = int(m.group("step"))
            self.status_data.latest_step_ms = int(m.group("ms"))
            return

        if m := RE_FACTOR_FOUND.search(line):
            self.status_data.factor_found = m.group("factor")
            self.status_data.factor_step = int(m.group("step"))
            return

        if m := RE_COMPOSITE_FACTOR.search(line):
            self.status_data.composite_factors.append(m.group("factor"))
            return

        if m := RE_PRIME_COFACTOR.search(line):
            self.status_data.prime_cofactors.append(m.group("cofactor"))
            return

    def time_remaining(self):
        if (
            self.start_time is None
            or self.status.run_current is None
            or self.status.run_total is None
            or self.status.run_current == 0
        ):
            return None

        delta = datetime.now() - self.start_time
        return (delta / self.status.run_current) * self.status.run_total


class EcmLog:
    def __init__(self, log_path): ...
