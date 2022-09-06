import statistics
from datetime import datetime


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

# Column alignment
ALIGN = [10, 14, 12, 12, 12]


class Lap:
    def __init__(self, total: datetime, *sectors: datetime, num=0):
        self.num = int(num)
        self.total = total
        self.sectors = sectors

    def __str__(self) -> str:
        return self.format()

    def format(self, num_align=ALIGN[0]) -> str:
        num = str(self.num) if self.num > 0 else ""

        output = num.ljust(num_align) + time_fmt(self.total).ljust(ALIGN[1])

        for idx, s in enumerate(self.sectors):
            align = ALIGN[2 + idx] if 2 + idx < len(ALIGN) else 10
            output += time_fmt(s).ljust(align)

        return output

    @classmethod
    def from_str(cls, num, total: str, *sectors: str):
        t = time_parse(total)
        s = [time_parse(s) for s in sectors]
        return cls(t, *s, num=int(num))

    def is_pit_lap(self) -> bool:
        return self.num in STINTS or self.num + 1 in STINTS


def time_fmt(time: datetime) -> str:
    return time.strftime("%M:%S.%f")[:-3]


def time_parse(string: str) -> datetime:
    return datetime.strptime(string, "%M:%S.%f")


def time_to_millis(time: datetime) -> int:
    return time.minute * 60 * 1000 + time.second * 1000 + time.microsecond // 1000


def millis_to_time(millis: int) -> datetime:
    return datetime.utcfromtimestamp(millis / 1000.0)


def average(laps: list[Lap]) -> Lap:
    totals: list[int] = []
    sectors: list[list[int]] = []

    for lap_idx, lap in enumerate(laps):
        totals.append(time_to_millis(lap.total))

        for sec_idx, sector in enumerate(lap.sectors):
            sector = time_to_millis(sector)
            if lap_idx == 0:
                sectors.append([sector])
            else:
                sectors[sec_idx].append(sector)

    total = millis_to_time(round(statistics.mean(totals)))
    avg_sectors = [millis_to_time(round(statistics.mean(sector))) for sector in sectors]

    return Lap(total, *avg_sectors)


def main():

    print("# STINTS:")

    # Print stints table
    for n, d in STINTS.items():
        print(f"{n:>5} -> {d}")

    laps: list[Lap] = []

    with open("laps.txt") as file:
        lines = file.readlines()

        for line in lines:
            parts = line.split()
            lap = Lap.from_str(parts[0], parts[1], parts[2], parts[3], parts[4])
            laps.append(lap)

    included: list[Lap] = []
    stint: list[Lap] = []
    averages = []
    last_driver = None

    print("\n" + "# LAPS:")

    for lap in laps:
        driver = STINTS.get(lap.num)
        if driver:
            if len(stint) != 0:
                # Calculate average times
                # print(average(stint))
                averages.append((last_driver, average(stint)))
                print()

            print(driver)
            stint.clear()
            last_driver = driver

        ignored = IGNORE_PIT_LAPS and lap.is_pit_lap()

        if not ignored:
            stint.append(lap)
            included.append(lap)

        # Display lap time
        print(lap, "*" if ignored else "")

    # Calculate average times for last stint
    # print(average(stint))
    averages.append((last_driver, average(stint)))

    print("\n" + "# AVERAGES:")

    for (d, avg) in averages:
        print(d.ljust(ALIGN[0]) + avg.format(num_align=0))

    print("total".ljust(ALIGN[0]) + average(included).format(num_align=0))


if __name__ == "__main__":
    main()
