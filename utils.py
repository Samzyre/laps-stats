from datetime import datetime, timedelta
from colorama import Fore, Back, Style


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


def average_time(time, n) -> datetime:
    try:
        return delta_to_time(time_to_delta(time) / n)
    except:
        return datetime.utcfromtimestamp(0)


# COLORING
def _static_color_fn(fg=""):
    @staticmethod
    def f(
        text: str,
        bg="",
        style="",
        reset_fg=False,
        reset_bg=False,
        reset_style=False,
    ) -> str:
        return Color.text(text, fg, bg, style, reset_fg, reset_bg, reset_style)

    return f


def _static_style_fn(style=""):
    @staticmethod
    def f(
        text: str,
        fg="",
        bg="",
        reset_fg=False,
        reset_bg=False,
        reset_style=False,
    ) -> str:
        return Color.text(text, fg, bg, style, reset_fg, reset_bg, reset_style)

    return f


class Color:
    @staticmethod
    def text(
        text: str,
        fg="",
        bg="",
        style="",
        reset_fg=False,
        reset_bg=False,
        reset_style=False,
    ) -> str:
        return (
            fg
            + bg
            + style
            + text
            + Color.reset(
                reset_fg,
                reset_bg,
                reset_style,
            )
        )

    @staticmethod
    def reset(
        fg=True,
        bg=True,
        style=True,
    ) -> str:
        r_fore = Fore.RESET if fg else ""
        r_back = Back.RESET if bg else ""
        r_style = Style.RESET_ALL if style else ""
        return r_fore + r_back + r_style

    black = _static_color_fn(Fore.BLACK)
    red = _static_color_fn(Fore.RED)
    green = _static_color_fn(Fore.GREEN)
    yellow = _static_color_fn(Fore.YELLOW)
    blue = _static_color_fn(Fore.BLUE)
    magenta = _static_color_fn(Fore.MAGENTA)
    cyan = _static_color_fn(Fore.CYAN)
    white = _static_color_fn(Fore.WHITE)
    light_black = _static_color_fn(Fore.LIGHTBLACK_EX)
    light_red = _static_color_fn(Fore.LIGHTRED_EX)
    light_green = _static_color_fn(Fore.LIGHTGREEN_EX)
    light_yellow = _static_color_fn(Fore.LIGHTYELLOW_EX)
    light_blue = _static_color_fn(Fore.LIGHTBLUE_EX)
    light_magenta = _static_color_fn(Fore.LIGHTMAGENTA_EX)
    light_cyan = _static_color_fn(Fore.LIGHTCYAN_EX)
    light_white = _static_color_fn(Fore.LIGHTWHITE_EX)

    dim = _static_style_fn(Style.DIM)
    normal = _static_style_fn(Style.NORMAL)
    bright = _static_style_fn(Style.BRIGHT)
