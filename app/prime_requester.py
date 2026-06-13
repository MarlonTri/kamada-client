import time
from client.kamada_client import KamadaClient
import multiprocessing
import threading


class PrimeRequester(object):
    def __init__(
        self, client : KamadaClient= None
    ):
        if client is None:
             self.client = KamadaClient()
        else: 
            self.client= client
        self.primes = []
        self.request_thread: threading.Thread = None
        self._terminate = False


    def start(self):
        self._terminate = False
        self.request_thread = threading.Thread(
            target=self._request_primes,
            daemon=True,
        )
        self.request_thread.start()

    def terminate(self):
        self._terminate = True
        time.sleep(1)
        # TODO -  add timer and max wait
        while self.request_thread.is_alive():
            time.sleep(5)
            print("Waiting for thread to exit....")
        print("Thread exited!!!")
        

    def _request_primes(self):
        prime_previews = self.client.get_all_prime_previews()
        for prime_preview in prime_previews:
            if self._terminate:
                print("Returning early", flush=True)
                return
            try:
                prime = self.client.get_prime(prime_preview.url)
            except Exception as e:
                print("Failed to retrieve prime: ", prime_preview, flush=True)
            print(f"Retrieved prime = {prime.url}", flush=True)
        print("Finished retrieving all primes!", flush=True)


def main():
    client = KamadaClient(request_delay_sec = 10)
    primeRequester = PrimeRequester(client=client)
    primeRequester.start()
    for i in range(30):
        time.sleep(1)
    primeRequester.terminate()



if __name__ == "__main__":
    main()

print()
