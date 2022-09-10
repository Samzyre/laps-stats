from re import S
import statistics

import colorama
from colorama import Fore, Back, Style

# import datetime
from datetime import datetime, timedelta

from enum import Enum, unique

from utils import *


# First lap number of each stint (:"driver")
STINTS = {
    1: "A",
    22: "B",
    44: "Bb",
    67: "Aa",
    90: "Aaa",
    113: "Bbb",
}

# In-laps and out-laps
IGNORE_PIT_LAPS = True

# Set color based on stint average, otherwise total average
COLOR_COMPARE_STINT = True

# Column alignment
ALIGN = [10, 14, 12, 12, 12]


@unique
class Diff(Enum):
    Neutral = 0
    Down = 1
    Up = 2


class Lap:
    def __init__(self, total: datetime, *sectors: datetime, num=0, diff=Diff.Neutral):
        self.num = int(num)
        self.total = total
        self.sectors = sectors
        self.diff = diff

    def __str__(self) -> str:
        return self.fmt()

    def __add__(self, other):
        if type(other) != Lap:
            return self

        total = delta_to_time(time_to_delta(self.total) + time_to_delta(other.total))

        sectors = [
            delta_to_time(time_to_delta(sec) + time_to_delta(other.sectors[idx]))
            for idx, sec in enumerate(self.sectors)
        ]

        return Lap(total, *sectors)

    __radd__ = __add__

    def fmt(self, align=ALIGN, hours=False) -> str:
        num = str(self.num) if self.num > 0 else ""

        if self.diff == Diff.Up:
            diff_color = Fore.GREEN
        elif self.diff == Diff.Down:
            diff_color = Fore.RED
        else:
            diff_color = Fore.WHITE

        output = (
            Fore.WHITE
            + num.ljust(align[0])
            + diff_color
            + time_fmt(self.total, hours).ljust(align[1])
            + Fore.RESET
        )

        for idx, s in enumerate(self.sectors):
            a = align[2 + idx] if 2 + idx < len(align) else 10
            output += time_fmt(s, hours).ljust(a)

        return output

    def is_pit_lap(self) -> bool:
        return self.num in STINTS or self.num + 1 in STINTS

    def set_diff_to(self, lap):
        this = time_to_delta(self.total)
        other = time_to_delta(lap.total)

        if this > other:
            self.diff = Diff.Down
        elif this < other:
            self.diff = Diff.Up
        else:
            self.diff = Diff.Neutral

    @classmethod
    def from_str(cls, num, total: str, *sectors: str):
        t = time_parse(total)
        s = [time_parse(s) for s in sectors]
        return cls(t, *s, num=int(num))

    @classmethod
    def zero(cls, n_sectors=3):
        s = ["00:00.000" for _ in range(0, n_sectors)]
        return cls.from_str(0, "00:00.000", *s)


class Stint:
    def __init__(self, name: str, laps: list[Lap]):
        self.name = name
        self.laps = laps
        self.avg = average(laps)
        self.included_avg = average(included(laps))

    def __str__(self) -> str:
        return self.fmt()

    def fmt(self, show_all=True) -> str:
        output = Fore.MAGENTA + self.name + "\n" + Fore.RESET

        for lap in self.laps:
            if COLOR_COMPARE_STINT:
                pass  # TODO

            lap.set_diff_to(self.included_avg)

            if not lap.is_pit_lap():
                output += str(lap) + "\n"
            elif lap.is_pit_lap() and show_all:
                output += Style.DIM + str(lap) + "*\n"

        return output


def included(laps: list[Lap]) -> list[Lap]:
    return [lap for lap in laps if not lap.is_pit_lap()]


def total(laps: list[Lap]):
    return sum(laps, start=Lap.zero())


def average(laps: list[Lap]) -> Lap:
    s = total(laps)
    n = len(laps)

    return Lap(
        average_time(s.total, n),
        *[average_time(t, n) for t in s.sectors],
    )


def stints(laps: list[Lap]) -> list[Stint]:
    last = laps[len(laps) - 1].num
    first = min(STINTS)

    laps_dict = {lap.num: lap for lap in laps}

    driver = None
    stints = []
    stint_laps = []

    for num in range(first, last + 1):
        switch = STINTS.get(num)

        if switch:
            if driver:
                stints.append(Stint(driver, stint_laps))
                stint_laps = []

            driver = switch

        found = laps_dict.get(num)

        if found:
            stint_laps.append(found)

    if len(stint_laps) > 0 and driver:
        stints.append(Stint(driver, stint_laps))

    return stints


class Stats:
    def __init__(self, laps: list[Lap]):
        self.laps = laps
        self.stints: list[Stint] = stints(laps)
        self.all_avg: Lap = average(laps)
        self.included_avg: Lap = average(included(laps))
        self.all_total = total(laps)
        self.included_total = total(included(laps))

    def __str__(self) -> str:
        return self.fmt()

    def fmt(
        self, stints=True, laps=True, show_all=True, averages=True, totals=True
    ) -> str:
        output = ""

        if stints:
            output += "# STINTS:\n"

            for n, d in STINTS.items():
                output += f"{n:>5} -> {d}\n"

            output += "\n"

        if laps:
            output += "# LAPS:\n"

            for stint in self.stints:
                output += stint.fmt(show_all) + "\n"

        if averages:
            output += "# AVERAGES:\n"

            for stint in self.stints:
                output += stint.included_avg.fmt() + "\n"

            output += "\n" + self.included_avg.fmt() + "\n"
            output += self.all_avg.fmt() + "\n\n"

        if totals:
            align = [n + 3 for n in ALIGN]
            align[0] = ALIGN[0]
            output += "# TOTALS:\n"
            output += self.included_total.fmt(align, hours=True) + "\n"
            output += self.all_total.fmt(align, hours=True) + "\n"

        return output


def main():

    laps: list[Lap] = []

    with open("laps.txt") as file:
        lines = file.readlines()

        for line in lines:
            parts = line.split()
            lap = Lap.from_str(parts[0], parts[1], parts[2], parts[3], parts[4])
            laps.append(lap)

    stats = Stats(laps)
    print(stats.fmt())


if __name__ == "__main__":
    colorama.init(autoreset=True)
    main()
    colorama.deinit()
