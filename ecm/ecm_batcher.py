from datetime import datetime
import logging
import docker
import threading
from typing import Optional
import time
from cachier import cachier
import os

from ecm.ecm_types import EcmStatus

DOCKER_CLIENT = docker.from_env()

ECM_CONTAINER_TAG = "ecm-batcher"
LOG_ROOT = "ecm_logs/"


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

        self.status = EcmStatus()
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
        self.status.start_time = datetime.now()

    def time_remaining(self):
        return self.status.time_remaining()

    def _consume_logs(self):
        for raw_line in self.container.logs(stream=True, follow=True):
            line = raw_line.decode("utf-8", errors="replace").strip()

            self.logs.append(line)
            self.status._parse_line(line)
            self.logger.info(line)

            # print(line)
            # TODO- save to log file.

        self.container.wait()

    def status(self) -> EcmStatus:
        return self.status

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
