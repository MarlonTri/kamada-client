from datetime import timedelta
import threading
import time
from typing import Dict

import concurrent

from client.kamada_client import KamadaClient
from client.kamada_types import KamadaPrime
from ecm.ecm_batcher import EcmContainer, estimate_cmd_time
from concurrent.futures import ThreadPoolExecutor

from ecm.ecm_types import EcmStatus


class Factorizer(object):
    def __init__(
        self,
        ecm_threads=3,
        request_primes_threads=1,
    ):

        self.client = KamadaClient()
        self.primes = []
        self.containers = []
        self.ecm_threads = ecm_threads
        self.request_primes_threads = request_primes_threads
        self.prime_estimates: Dict[str, timedelta] = dict()
        self.prime_runs = dict()
        self._start_non_ecm_threads()
        self.ecm_loop()

    def ecm_loop(self):

        # Submit tasks and store the returned 'Future' objects
        containers = []
        while True:
            while len(containers) < self.ecm_threads:
                primes = self.client.get_cached_primes()
                primes = [p for p in primes if p.tag not in self.prime_runs]
                prime = primes[0]
                print("Adding prime: ", prime.tag)
                self.prime_runs[prime.tag] = ...
                cmd = prime.ecm_commands[prime.ecm_tot_effort.level].command
                container = EcmContainer(cmd, prime.tag)
                container.start()
                containers.append(container)

            time.sleep(30)

            for i, container in enumerate(containers):
                if container.status().finished:
                    del containers[i]
                    break

    def _start_non_ecm_threads(self):
        assert self.request_primes_threads <= 1

        self.request_thread = threading.Thread(
            target=self._request_primes,
            daemon=True,
        )
        if self.request_primes_threads:
            self.request_thread.start()

    def _request_primes(self):
        prime_previews = self.client.get_all_prime_previews()
        for prime_preview in prime_previews:
            try:
                prime = self.client.get_prime(prime_preview.url)
            except Exception as e:
                print("Failed to retrieve prime: ", prime_preview)
            print(f"Retrieved prime = {prime.url}")
        print("EXITING _request_primes FUNCTION!!!")


def main():

    factorizer = Factorizer(ecm_threads=8, request_primes_threads=True)
    # primes = factorizer.client.get_cached_primes()
    # factorizer._estimate_primes()

    for i in range(1000):
        time.sleep(30)
        print("sleep ", i)


if __name__ == "__main__":
    main()

print()
