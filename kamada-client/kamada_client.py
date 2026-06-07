# import the necessary libraries
from bs4 import BeautifulSoup
import requests
from kamada_types import *

# make a GET request to the target website
response = requests.get("https://stdkmd.net/nrr/abbbc.htm")
# retrieve the response
html = response.text

# create a BeautifulSoup object
soup = BeautifulSoup(html)

# select the table element
table = soup.find("table")

# extract headers
headers = [th.text.strip() for th in table.find_all("th")]

# extract table body
rows = []
for row in table.find_all("tr")[1:]:
    cells = row.find_all("td")
    assert len(cells) == 5

    href = cells[0].find("a")
    n_range = cells[2].text
    subcells = cells[3].find_all("a")
    family_primes = []
    for subcell in subcells:
        ecm_classes = subcell["class"]
        assert len(ecm_classes) == 1
        family_primes.append(KamadaFamilyPrime(n=subcell.text, ecm_n=ecm_classes[0]))
    row = KamadaFamilyRow(
        href=href, n_range=n_range, primes=family_primes, last_updated=None
    )  # TODO
    rows.append(row)

# log data
print("Headers:", headers)
print("table_body:")
for row in rows:
    print(row)
