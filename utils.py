from datetime import datetime, timedelta


def time_to_delta(time: datetime) -> timedelta:
    return timedelta(
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
        microseconds=time.microsecond,
    )


def delta_to_time(time: timedelta) -> datetime:
    return datetime.utcfromtimestamp(time.total_seconds())


def time_fmt(time: datetime, hours=False) -> str:
    if hours:
        return time.strftime("%H:%M:%S.%f")[:-3]
    else:
        return time.strftime("%M:%S.%f")[:-3]


def time_parse(string: str, hours=False) -> datetime:
    if hours:
        return datetime.strptime(string, "%H:%M:%S.%f")
    else:
        return datetime.strptime(string, "%M:%S.%f")


def time_to_millis(time: datetime) -> int:
    return (
        time.minute * 60 * 1000 + time.second * 1000 + round(time.microsecond / 1000.0)
    )


def millis_to_time(millis: int) -> datetime:
    return datetime.utcfromtimestamp(millis / 1000.0)


def average_time(time, n) -> datetime:
    return millis_to_time(round(time_to_millis(time) / n))