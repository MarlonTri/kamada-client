import re

RE_VERSION = re.compile(r"(?P<version>GMP-ECM \d+\.\d+\.\d+ .*?\[ECM\])")
RE_INPUT = re.compile(r"Input number is (?P<number>\d+) \((?P<digits>\d+) digits\)")
RE_USING = re.compile(
    r"Using B1=(?P<B1>\d+), B2=(?P<B2>\d+), polynomial (?P<polynomial>\w+\(\d+\)), sigma=(?P<sigma>[\d:]+)"
)
RE_RUN = re.compile(r"Run (?P<current>\d+) out of (?P<total>\d+):")
RE_STEP = re.compile(r"Step (?P<step>\d+) took (?P<ms>\d+)ms")
RE_PRIME_FACTOR = re.compile(
    r"Found prime factor of (?P<digits>\d+) digits: (?P<factor>\d+)"
)
RE_COMPOSITE_FACTOR = re.compile(
    r"Found composite factor of (?P<digits>\d+) digits: (?P<factor>\d+)"
)
RE_PRIME_COFACTOR = re.compile(
    r"Prime cofactor (?P<cofactor>\d+) has (?P<digits>\d+) digits"
)
RE_COMPOSITE_COFACTOR = re.compile(
    r"Composite cofactor (?P<cofactor>\d+) has (?P<digits>\d+) digits"
)
RE_FACTOR_FOUND = re.compile(r"\*+ Factor found in step (?P<step>\d+): (?P<factor>\d+)")
