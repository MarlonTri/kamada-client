from ast import List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict


class EcmLevel(Enum):
    ECM_35 = "ecm35"
    ECM_40 = "ecm40"
    ECM_45 = "ecm45"
    ECM_50 = "ecm50"
    ECM_55 = "ecm55"
    ECM_60 = "ecm60"
    ECM_65 = "ecm65"


class Status(Enum):
    FREE_TO_FACTOR = "Free to factor"
    RESERVED = "Reserved"
    COMPLETED = "Completed"


@dataclass
class PrimeExpression:
    expr: str


@dataclass
class EcmCommand:
    level: EcmLevel
    command: str


@dataclass
class EcmEffort:
    level: EcmLevel
    b1: str
    runs: int
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
class KamadaPrimePreview:
    n: int
    ecm_level: EcmLevel
    url: str


@dataclass
class KamadaFamilyRow:
    href: str
    n_range: str
    primes: List[KamadaPrimePreview]
    last_updated: datetime


@dataclass
class KamadaFamily:
    rows: List[KamadaFamilyRow]

    def get_primes(self):
        primes = []
        for row in self.rows:
            primes += row.primes

        assert len(primes) != 0

        return primes


class KamadaPrime:

    def __init__(
        self, url, expr, code, composite_factor, status, ecm_commands, ecm_efforts
    ):
        self.url: str = url
        self.expr: PrimeExpression = expr
        self.code: str = code
        self.composite_factor: int = composite_factor
        self.status: Status = status
        self.ecm_commands: Dict[EcmLevel, EcmCommand] = ecm_commands
        self.ecm_efforts: List[EcmEffort] = ecm_efforts
        self.ecm_level: EcmLevel = None
        self.ecm_tot_effort: EcmEffort = None
        self._init_fields()

    def _init_fields(self) -> EcmLevel:

        for ecm_level in EcmLevel:
            efforts = [x for x in self.ecm_efforts if x.level == ecm_level]

            if len(efforts) == 0:
                continue
            efforts = [x for x in efforts if x.total_runs is not None]
            assert len(efforts) == 1

            tot_effort = efforts[0]

            if tot_effort.total_runs >= tot_effort.required_runs:
                continue

            self.ecm_level = ecm_level
            self.ecm_tot_effort = tot_effort
            self.tag = self.url.split("=")[-1]
            return

        raise ValueError()
