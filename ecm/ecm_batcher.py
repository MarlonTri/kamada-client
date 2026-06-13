from datetime import datetime
import logging
import docker
import threading
import re
from dataclasses import dataclass, field
from typing import Optional
import time
from cachier import cachier
import os

DOCKER_CLIENT = docker.from_env()

ECM_CONTAINER_TAG = "ecm-batcher"
LOG_ROOT = "ecm_logs/"

RE_VERSION = re.compile(r"(?P<version>GMP-ECM \d+\.\d+\.\d+ .*?\[ECM\])")

RE_INPUT = re.compile(r"Input number is (?P<number>\d+) \((?P<digits>\d+) digits\)")

RE_USING = re.compile(
    r"Using B1=(?P<B1>\d+), B2=(?P<B2>\d+), polynomial (?P<polynomial>\w+\(\d+\)), sigma=(?P<sigma>[\d:]+)"
)

RE_RUN = re.compile(r"Run (?P<current>\d+) out of (?P<total>\d+):")

RE_STEP = re.compile(r"Step (?P<step>\d+) took (?P<ms>\d+)ms")

RE_FACTOR_FOUND = re.compile(r"\*+ Factor found in step (?P<step>\d+): (?P<factor>\d+)")

RE_COMPOSITE_FACTOR = re.compile(
    r"Found composite factor of (?P<digits>\d+) digits: (?P<factor>\d+)"
)

RE_PRIME_COFACTOR = re.compile(
    r"Prime cofactor (?P<cofactor>\d+) has (?P<digits>\d+) digits"
)


@dataclass
class EcmStatus:
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

    composite_factor: Optional[str] = None
    prime_cofactor: Optional[str] = None

    finished: bool = False


def make_logger(logger_tag):

    # 1. Create a logger specific to this task/function
    logger = logging.getLogger(logger_tag)
    logger.setLevel(logging.INFO)

    # 2. Prevent logs from propagating to the root/main logger (optional)
    logger.propagate = False

    # 3. Add a FileHandler for this specific file
    if not logger.handlers:
        logger_path = os.path.join(LOG_ROOT, logger_tag + ".log")
        fh = logging.FileHandler(logger_path)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


class EcmContainer:
    def __init__(self, command: str, logger_tag=None):
        self.command_raw = command
        self.command = f"sh -c '{command}'"

        self.logger_tag = logger_tag

        self.container = None
        self.thread = None

        self.status_data = EcmStatus()
        self.logs = []
        self.start_time = None
        self.logger = make_logger(self.logger_tag)

    def start(self, remove=True):
        print(f"Starting ECM container with command:\n\t{self.command_raw}")
        self.container = DOCKER_CLIENT.containers.run(
            ECM_CONTAINER_TAG, self.command, detach=True, remove=remove
        )
        self.thread = threading.Thread(
            target=self._consume_logs,
            daemon=True,
        )
        self.thread.start()
        self.start_time = datetime.now()

    def time_remaining(self):
        if (
            self.start_time is None
            or self.status_data.run_current is None
            or self.status_data.run_total is None
            or self.status_data.run_current == 0
        ):
            return None

        delta = datetime.now() - self.start_time
        return (delta / self.status_data.run_current) * self.status_data.run_total

    def _consume_logs(self):
        for raw_line in self.container.logs(stream=True, follow=True):
            line = raw_line.decode("utf-8", errors="replace").strip()

            self.logs.append(line)
            self._parse_line(line)
            self.logger.info(line)

            # print(line)
            # TODO- save to log file.

        self.container.wait()
        self.status_data.finished = True

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
            self.status_data.composite_factor = m.group("factor")
            return

        if m := RE_PRIME_COFACTOR.search(line):
            self.status_data.prime_cofactor = m.group("cofactor")
            return

    def status(self) -> EcmStatus:
        return self.status_data

    def is_running(self):
        if self.container is None:
            return False

        self.container.reload()
        return self.container.status == "running"

    def wait(self):
        if self.thread:
            self.thread.join()

    def stop(self):
        if self.container:
            self.container.stop()


# -----------------------
# Example usage
# -----------------------

if __name__ == "__main__":

    cmd = "echo 32216116878907409440017505568597510389177085596212434976182286570054026250184062917061084197646760111727148674121826585853660376768262325565613913 | ecm -c 3882 11e6"

    ecm = EcmContainer(cmd)
    ecm.start()

    while ecm.is_running():
        s = ecm.status()

        print(
            f"run={s.run_current}/{s.run_total} "
            f"step={s.latest_step} "
            f"time_remaining={ecm.time_remaining()} "
        )

        import time

        time.sleep(30)

    ecm.wait()

    print(ecm.status())
