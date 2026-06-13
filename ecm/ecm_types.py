# class EcmLogLine()

from ecm.ecm_re_types import (
    RE_COMPOSITE_FACTOR,
    RE_FACTOR_FOUND,
    RE_INPUT,
    RE_PRIME_COFACTOR,
    RE_PRIME_FACTOR,
    RE_RUN,
    RE_STEP,
    RE_USING,
    RE_VERSION,
    RE_COMPOSITE_COFACTOR,
)


from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class EcmStatus:
    def __init__(self):

        self.start_time: Optional[datetime] = None
        self.version: Optional[str] = None

        self.input_number: Optional[str] = None
        self.input_digits: Optional[int] = None

        self.run_current: Optional[int] = None
        self.run_total: Optional[int] = None

        self.B1: Optional[int] = None
        self.B2: Optional[int] = None
        self.polynomial: Optional[str] = None
        self.sigma: Optional[str] = None

        self.latest_step: Optional[int] = None
        self.latest_step_ms: Optional[int] = None

        self.factor_found: Optional[str] = None
        self.factor_step: Optional[int] = None

        self.composite_factors: List[str] = []
        self.prime_factors: List[str] = []
        self.prime_cofactors: List[str] = []
        self.composite_cofactors: List[str] = []

    def parse_line(self, line: str):
        if m := RE_VERSION.search(line):
            self.version = m.group("version")
            return m

        if m := RE_INPUT.search(line):
            self.input_number = m.group("number")
            self.input_digits = int(m.group("digits"))
            return m

        if m := RE_RUN.search(line):
            self.run_current = int(m.group("current"))
            self.run_total = int(m.group("total"))
            return m

        if m := RE_USING.search(line):
            self.B1 = int(m.group("B1"))
            self.B2 = int(m.group("B2"))
            self.polynomial = m.group("polynomial")
            self.sigma = m.group("sigma")
            return m

        if m := RE_STEP.search(line):
            self.latest_step = int(m.group("step"))
            self.latest_step_ms = int(m.group("ms"))
            return m

        if m := RE_FACTOR_FOUND.search(line):
            self.factor_found = m.group("factor")
            self.factor_step = int(m.group("step"))
            return m

        if m := RE_COMPOSITE_FACTOR.search(line):
            self.composite_factors.append(m.group("factor"))
            return m

        if m := RE_PRIME_FACTOR.search(line):
            self.prime_factors.append(m.group("factor"))
            return m

        if m := RE_PRIME_COFACTOR.search(line):
            self.prime_cofactors.append(m.group("cofactor"))
            return m

        if m := RE_COMPOSITE_COFACTOR.search(line):
            self.composite_cofactors.append(m.group("cofactor"))
            return m

        # if not line:
        #    return m

        raise ValueError("Weird ECM line --> " + line)

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
    def __init__(self, log_text: str = None, log_path: str = None):
        # todo
        if log_path is not None:
            assert log_text is None
            with open(log_path, "r") as f:
                log_text = f.read()

        assert log_text is not None
        log_text = log_text.strip()

        self.text: str = log_text
        self.status: EcmStatus = EcmStatus()
        self.prime_finds: Dict[int, List[str]] = dict()
        self.complete = False

        self._parse_log()
        self._calc_completed()

    def _parse_log(self):
        lines = self.text.split("\n")
        for i, line in enumerate(lines):
            m = self.status.parse_line(line)
            if m is None:
                continue
            matches = m.groupdict()
            if "cofactor" in matches:
                tail = "\n".join(lines[i - 6 : i + 1])
                self.prime_finds[i] = tail

    def _calc_completed(self):
        if self.status.run_current == self.status.run_total:
            self.complete = True
            return

        if self.text.count("\n") in self.prime_finds:
            self.complete = True
            return

        self.complete = False


if __name__ == "__main__":
    test_log_paths = [
        "69994_243.log",
        "69995_228.log",
        "89992_276.log",
        "78885_290.log",
    ]

    for log_path in test_log_paths:
        log_path = "ecm_logs/" + log_path

        ecm_log = EcmLog(log_path=log_path)

        print("ecm_log = ", log_path)
        for line, find in ecm_log.prime_finds.items():
            print("prime find on line: ", line)
            print("\t" + find.replace("\n", "\n\t"))
        print(f"{ecm_log.complete=}")
        print()
