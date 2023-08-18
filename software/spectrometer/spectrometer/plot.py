import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def format_for_thesis(axes: Axes) -> None:
    """Adjust the style of the axes for a thesis

    Note: The axes should have been created with the `make_subplots(...)` function in this module
    for optimal layout

    Note: This function has side effects (it sets global matplotlib options!). This might lead to
    confusingly formatted graphs later on if you change the style.

    Args:
        axes (Axes): Axes to style
    """

    # Adjust axis
    axes.spines[["top", "right"]].set_visible(False)
    axes.spines[["left", "bottom"]].set_position(("outward", 20))
    plt.setp(
        [
            *axes.lines,
            *axes.tables,
            *axes.artists,
            *axes.images,
            *axes.patches,
            *axes.texts,
            *axes.collections,
        ],
        clip_on=False,
    )

    # Set axis colour to ETH Grey
    color = "#575757"  # normal grey: "#6F6F6F", dark grey: "#575757"
    axes.tick_params(colors=color)
    axes.spines[["left", "bottom", "top", "right"]].set_color(color)
    axes.xaxis.label.set_color(color)
    axes.yaxis.label.set_color(color)

    # Change font
    plt.setp(
        [
            axes.title,
            axes.xaxis.label,
            axes.yaxis.label,
            *axes.get_xticklabels(),
            *axes.get_yticklabels(),
            *(axes.get_legend().get_texts() if axes.get_legend() else ()),
        ],
        family=["Tex Gyre Pagella"],
    )

    # Adjust ticks
    axes.tick_params(axis="both", direction="in")


def subplots(
    rows: int = 1, columns: int = 1, **kwargs
) -> tuple[Figure, Axes | list[Axes]]:
    if rows < 1:
        msg = "Number of rows must be positive"
        raise ValueError(msg)
    if columns < 1:
        msg = "Number of columns must be positive"
        raise ValueError(msg)

    plt.rcParams["axes.autolimit_mode"] = "round_numbers"
    plt.rcParams["axes.xmargin"] = 0
    plt.rcParams["axes.ymargin"] = 0

    fig, axes = plt.subplots(
        nrows=rows,
        ncols=columns,
        layout="constrained",  # Alternative: tight_layout=True
        **kwargs,
    )

    return fig, axes


def style_axes(
    axes: Axes,
    nticks: int = 2,
    xunit: str = "",
    yunit: str = "",
    *,
    serif: bool = False,
) -> None:
    """Style axes inspired by Principae/Tufte

    Args:
        axes (Axes): Matplotlib Axes object to apply the style to
        nticks (int, optional): Number of ticks on the spines/axis. Defaults to 2 (start/end).
        xunit (str, optional): Unit of the x-Axis. Defaults to "".
        yunit (str, optional): Unit of the y-Axis. Defaults to "".
    """
    _adjust_spines(axes)
    _adjust_ticks(axes, nticks, xunit, yunit)
    _adjust_axis_color(axes)
    _adjust_fonts(axes, serif=serif)
    axes.figure.tight_layout()


def _adjust_spines(axes: Axes) -> None:
    """Push the spines (i.e. x/y Axis) outward"""
    axes.spines[["top", "right"]].set_visible(False)
    axes.spines[["left", "bottom"]].set_position(("outward", 20))
    _remove_margins(axes)


def _remove_margins(axes: Axes) -> None:
    """Remove margins around one "graph" i.e. axes object"""
    axes.margins(0)
    plt.setp(
        [
            *axes.lines,
            *axes.tables,
            *axes.artists,
            *axes.images,
            *axes.patches,
            *axes.texts,
            *axes.collections,
        ],
        clip_on=False,
    )


def _adjust_fonts(axes: Axes, *, serif: bool = False) -> None:
    wanted_fonts_sans = [
        "Latin Modern Sans",
        "CMU Sans Serif",
        "Computer Modern Sans Serif",
        "Lucida Sans",
        "Luxi Sans",
        "Noto Sans",
        *plt.rcParams["font.sans-serif"],
    ]
    wanted_fonts_serif = [
        "Latin Modern Roman",
        "CMU Serif",
        "Computer Modern Serif",
        "Lucida Bright",
        "Luxi Serif",
        "Noto Serif",
        *plt.rcParams["font.serif"],
    ]
    wanted_fonts = wanted_fonts_serif if serif else wanted_fonts_sans
    available_fonts = mpl.font_manager.get_font_names()
    fonts = [font for font in wanted_fonts if font in available_fonts]

    plt.setp(
        [
            axes.title,
            axes.xaxis.label,
            axes.yaxis.label,
            *axes.get_xticklabels(),
            *axes.get_yticklabels(),
            *(axes.get_legend().get_texts() if axes.get_legend() else ()),
        ],
        family=fonts,
    )


def _adjust_ticks(
    axes: Axes, nticks: int = 2, xunit: str = "", yunit: str = "", unit_sep: str = " "
) -> None:
    _adjust_xticks(axes, nticks, xunit, unit_sep)
    _adjust_yticks(axes, nticks, yunit, unit_sep)
    axes.tick_params(axis="both", direction="in")


def _adjust_xticks(axes: Axes, nticks: int, xunit: str, unit_sep: str):
    axes.xaxis.set_major_locator(ticker.LinearLocator(nticks))
    axes.xaxis.set_major_formatter(
        _LastTickScalarFormatter((unit_sep if xunit else "") + xunit)
    )


def _adjust_yticks(axes: Axes, nticks: int, yunit: str, unit_sep: str):
    axes.yaxis.set_major_locator(ticker.LinearLocator(nticks))
    axes.yaxis.set_major_formatter(
        _LastTickScalarFormatter((unit_sep if yunit else "") + yunit)
    )


def _adjust_axis_color(axes: Axes, color: str = "gray"):
    # use `color` (without s) to only color the ticks (not the labels)
    axes.tick_params(colors=color)
    axes.spines[["left", "bottom", "top", "right"]].set_color(color)
    axes.xaxis.label.set_color(color)
    axes.yaxis.label.set_color(color)


class _LastTickScalarFormatter(ticker.ScalarFormatter):
    def __init__(
        self,
        unit: str = "",
        useOffset: bool | float | None = None,  # noqa: N803
        useMathText: bool | None = None,  # noqa: N803
        useLocale: bool | None = None,  # noqa: N803
    ) -> None:
        super().__init__(useOffset, useMathText, useLocale)
        self.unit = unit

    def __call__(self, x: float, pos: int | None = None) -> str:
        res = super().__call__(x, pos)
        if x == self.locs[-1]:
            res += self.unit
        return res
