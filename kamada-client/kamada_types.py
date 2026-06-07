from ast import List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Status(Enum):
    FREE_TO_FACTOR = 1
    RESERVED = 2
    COMPLETED = 3


@dataclass
class PrimeExpression:
    expr: str


@dataclass
class EcmCommand:
    digits: int
    command: str


@dataclass
class EcmEffort:
    level: int
    b1: str
    total_runs: int
    required_runs: int
    name: str
    date: datetime


@dataclass
class EcmContribution:
    results: str
    software: str
    exec_env: str
    reservation_key: str
    name: str
    date: datetime


@dataclass
class KamadaFamilyPrime:
    n: int
    ecm_n: int


@dataclass
class KamadaFamilyRow:
    href: str
    n_range: str
    primes: List[KamadaFamilyPrime]
    last_updated: datetime


@dataclass
class KamadaPrime:
    expr: PrimeExpression
    code: str
    composite_factor: int
    status: Status
    ecm_commands: List[EcmCommand]
    ecm_efforts: List[EcmEffort]
