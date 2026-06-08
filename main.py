from client.kamada_client import KamadaClient
from ecm.ecm_batcher import EcmContainer


def main():
    print("Hello from kamada-api!")
    client = KamadaClient()
    prime_previews = client.get_all_prime_previews()
    primes = client.get_cached_primes()
    primes.sort(
        key=lambda p: (p.ecm_tot_effort.total_runs != 0, p.ecm_tot_effort.required_runs)
    )
    print()


if __name__ == "__main__":
    main()
