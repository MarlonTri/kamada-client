import random
import time
from typing import Dict

from requests_cache import CachedSession
from datetime import timedelta
from client.kamada_client_util import parse_kamada_family, parse_kamada_prime, time_it
from client.kamada_types import EcmLevel, KamadaFamily, KamadaPrime

DEFAULT_SEED: int = 0xCAFEBEEF


class KamadaClient(object):
    PRIME_FAMILY_URLS: Dict[str, str] = {"ABBBC": "https://stdkmd.net/nrr/abbbc.htm"}

    def __init__(
        self,
        cache_name="cache/KAMADA_CLIENT_CACHE",
        cache_expire_after_days=None,
        request_delay_sec=60,
    ):

        if cache_expire_after_days is None:
            cache_expire_after = None
        else:
            cache_expire_after = timedelta(days=cache_expire_after_days)
        self.request_delay_sec = request_delay_sec
        self._session = CachedSession(
            cache_name, expire_after=cache_expire_after, backend="filesystem"
        )
        self.last_request = 0

    def request_get(self, url, force_refresh):

        if self.request_delay_sec and not self._session.cache.contains(url):
            now = time.time()
            time_since_last_req = now - self.last_request
            if time_since_last_req < self.request_delay_sec:
                print(
                    f"Uncached req found. {time_since_last_req=} sec. Waiting {self.request_delay_sec - time_since_last_req} sec"
                )
                time.sleep(self.request_delay_sec - time_since_last_req)

        response = self._session.get(url, force_refresh=force_refresh)

        if not response.from_cache:
            self.last_request = time.time()

        return response

    def get_prime_family(self, url, force_refresh=False) -> KamadaFamily:
        response = self.request_get(url, force_refresh=force_refresh)
        return parse_kamada_family(response.text)

    @time_it
    def get_prime(self, url, force_refresh=False) -> KamadaPrime:
        response = self.request_get(url, force_refresh=force_refresh)
        return parse_kamada_prime(url, response.text)

    def get_cached_primes(self):
        responses = list(self._session.cache.filter())
        responses = [r for r in responses if "https://stdkmd.net/nrr/c.cgi" in r.url]
        primes = []

        for r in responses:
            try:
                prime = parse_kamada_prime(r.url, r.text)
            except Exception as e:
                pass
            primes.append(prime)

        primes.sort(
            key=lambda p: (
                p.ecm_tot_effort.total_runs != 0,
                p.ecm_tot_effort.required_runs,
            )
        )
        return primes

    @time_it
    def get_all_prime_previews(
        self,
        ecm_filter=EcmLevel.ECM_40,
        shuffle=True,
        seed=DEFAULT_SEED,
        force_refresh=False,
    ):
        primes = []
        for _, url in self.PRIME_FAMILY_URLS.items():
            family: KamadaFamily = self.get_prime_family(
                url, force_refresh=force_refresh
            )
            primes += family.get_primes()

        if ecm_filter is not None:
            primes = [prime for prime in primes if prime.ecm_level == ecm_filter]

        assert len(primes) != 0
        if shuffle:
            rng = random.Random(seed)
            rng.shuffle(primes)
        return primes
