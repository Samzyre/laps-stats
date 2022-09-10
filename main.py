# import statistics
import colorama

# import datetime
from datetime import datetime

from enum import Enum, unique

from utils import (
    time_to_delta,
    delta_to_time,
    time_fmt,
    time_parse,
    average_time,
    Color,
)


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
ALIGN = [14, 14, 12, 12, 12]


@unique
class Diff(Enum):
    Neutral = 0
    Down = 1
    Up = 2


class Lap:
    def __init__(
        self,
        total: datetime,
        *sectors: datetime,
        num=0,
        diff=Diff.Neutral,
        sector_diffs=[],
    ):
        self.num = int(num)
        self.total = total
        self.sectors = sectors
        self.diff = diff
        self.sector_diffs = [Diff.Neutral for _ in sectors]

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
            diff_color = Color.green
        elif self.diff == Diff.Down:
            diff_color = Color.red
        else:
            diff_color = Color.white

        output = Color.white(num.ljust(align[0])) + diff_color(
            time_fmt(self.total, hours).ljust(align[1]) + Color.reset(style=False)
        )

        for idx, s in enumerate(self.sectors):
            a = align[2 + idx] if 2 + idx < len(align) else 10

            if self.sector_diffs[idx] == Diff.Up:
                diff_color = Color.green
            elif self.sector_diffs[idx] == Diff.Down:
                diff_color = Color.red
            else:
                diff_color = Color.white

            output += diff_color(time_fmt(s, hours).ljust(a)) + Color.reset(style=False)

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

        for idx, this_sector in enumerate(self.sectors):
            this = time_to_delta(this_sector)
            other = time_to_delta(lap.sectors[idx])

            if this > other:
                self.sector_diffs[idx] = Diff.Down
            elif this < other:
                self.sector_diffs[idx] = Diff.Up
            else:
                self.sector_diffs[idx] = Diff.Neutral

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
        output = Color.magenta(self.name + "\n")

        for lap in self.laps:
            if not lap.is_pit_lap():
                output += Color.bright(str(lap) + "\n")
            elif lap.is_pit_lap() and show_all:
                output += Color.dim(str(lap) + "*\n")

        return output

    def set_diff_to(self, lap: None | Lap = None):
        for l in self.laps:
            if lap:
                l.set_diff_to(lap)
            else:
                l.set_diff_to(self.included_avg)


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
                if COLOR_COMPARE_STINT:
                    stint.set_diff_to(stint.included_avg)
                else:
                    stint.set_diff_to(self.included_avg)

                output += stint.fmt(show_all) + "\n"

        if averages:
            output += "# AVERAGES:\n"

            align = [0, *ALIGN[1:]]

            for stint in self.stints:
                name = stint.name.ljust(ALIGN[0])
                lap = stint.included_avg
                lap.set_diff_to(self.included_avg)
                output += Color.magenta(name) + lap.fmt(align) + "\n"

            output += "\n"
            output += "incl. avg".ljust(ALIGN[0]) + self.included_avg.fmt(align) + "\n"
            output += "total avg".ljust(ALIGN[0]) + self.all_avg.fmt(align) + "\n\n"

        if totals:
            output += "# TOTALS:\n"

            align = [0, *[n + 3 for n in ALIGN[1:]]]

            output += (
                "incl. total".ljust(ALIGN[0])
                + self.included_total.fmt(align, hours=True)
                + "\n"
            )
            output += (
                "full total".ljust(ALIGN[0])
                + self.all_total.fmt(align, hours=True)
                + "\n"
            )

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
