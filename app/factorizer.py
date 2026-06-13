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
    ):

        self.client = KamadaClient()
        self.primes = []
        self.containers = []
        self.ecm_threads = ecm_threads
        self.prime_runs = dict()
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


def main():

    factorizer = Factorizer(ecm_threads=8)
    # primes = factorizer.client.get_cached_primes()
    # factorizer._estimate_primes()

    for i in range(1000):
        time.sleep(30)
        print("sleep ", i)


if __name__ == "__main__":
    main()

print()
