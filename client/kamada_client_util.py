# import the necessary libraries
from functools import wraps
import re
import time

from bs4 import BeautifulSoup
from client.kamada_types import *

RE_FAMILY_HREF = re.compile(r"(?P<start>\d)/(?P<family>\d+)\.htm")

PRIME_FAMILY_URLS = ["https://stdkmd.net/nrr/abbbc.htm"]


def get_prime_url(family_href: str, prime_n: int):
    m = RE_FAMILY_HREF.search(family_href)
    assert m
    family = m.group("family")
    return f"https://stdkmd.net/nrr/c.cgi?q={family}_{prime_n}"


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result

    return wrapper


def parse_kamada_family(html) -> KamadaFamily:

    soup = BeautifulSoup(html, features="html.parser")

    # select the table element
    table = soup.find("table")

    # extract table body
    rows = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        assert len(cells) == 5

        href = cells[0].find("a")["href"]
        n_range = cells[2].text
        subcells = cells[3].find_all("a")
        family_primes = []
        for subcell in subcells:
            ecm_classes = subcell["class"]
            assert len(ecm_classes) == 1
            ecm_level = EcmLevel(ecm_classes[0])
            n = subcell.text
            family_primes.append(
                KamadaPrimePreview(n=n, ecm_level=ecm_level, url=get_prime_url(href, n))
            )
        row = KamadaFamilyRow(
            href=href, n_range=n_range, primes=family_primes, last_updated=...
        )
        rows.append(row)
    return KamadaFamily(rows=rows)


def parse_ecm_commands(soup) -> Dict[EcmLevel, EcmCommand]:
    elements = soup.find(id="body").find_all(recursive=False)
    ecm_commands = dict()
    for i in range(len(elements) - 1):
        ele1 = elements[i]
        ele2 = elements[i + 1]
        if ele1.name == "h4" and ele2.name == "pre":
            level = ele1.find("span", {"class": "en"})
            level = "ecm" + level.text.split("-")[0]
            level = EcmLevel(level)
            ecm_command = EcmCommand(level=level, command=ele2.text)
            ecm_commands[level] = ecm_command
    return ecm_commands


def parse_ecm_efforts(soup):
    form = soup.find_all("form")[0]
    table = form.find_all("table")
    assert len(table) == 1
    table = table[0]

    trs = table.find_all("tr")[1:]
    ecm_level: str = None
    b1: str = None
    ecm_efforts = []
    for tr in trs:
        tds = tr.find_all("td")
        assert len(tds) in [3, 5]
        if len(tds) == 5:
            ecm_level = tds[0]["class"][0]
            b1 = tds[1].text
            del tds[0:2]

        runs_raw = tds[0].text.split(" / ")
        assert len(runs_raw) in [1, 2]

        if len(runs_raw) == 1:
            runs = int(runs_raw[0])
            total_runs = None
            required_runs = None
        else:
            runs = None
            if runs_raw[0]:
                total_runs = int(runs_raw[0])
            else:
                total_runs = None
            required_runs = int(runs_raw[1].split()[0])

        name = tds[1].text
        date = ...
        ecm_effort = EcmEffort(
            level=EcmLevel(ecm_level),
            b1=b1,
            runs=runs,
            total_runs=total_runs,
            required_runs=required_runs,
            name=name,
            date=date,
        )
        ecm_efforts.append(ecm_effort)

    return ecm_efforts


def parse_kamada_prime(url, html) -> KamadaPrime:
    # create a BeautifulSoup object
    soup = BeautifulSoup(html, features="html.parser")

    expr = soup.find_all("p")[0]
    composite_factor = soup.find_all("p")[1].find("span").text
    status_raw = soup.find("span", {"class": "x"}).text
    status = Status(status_raw)
    ecm_commands = parse_ecm_commands(soup)
    ecm_efforts = parse_ecm_efforts(soup)

    return KamadaPrime(
        url=url,
        expr=expr,
        code=...,
        composite_factor=composite_factor,
        status=status,
        ecm_commands=ecm_commands,
        ecm_efforts=ecm_efforts,
    )
