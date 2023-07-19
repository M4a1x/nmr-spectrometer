from typing import Optional

import matplotlib as mpl
from cycler import cycler
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np

# TODO: Look at matplotx/mplx dufte style - might be better


def make_axes(
    rows: int = 1, columns: int = 1, **kwargs
) -> tuple[Figure, Axes | list[Axes]]:
    if rows < 1:
        msg = "Number of rows must be positive"
        raise ValueError(msg)
    if columns < 1:
        msg = "Number of columns must be positive"
        raise ValueError(msg)

    plt.rcParams["axes.autolimit_mode"] = "round_numbers"

    fig, axes = plt.subplots(
        nrows=rows,
        ncols=columns,
        figsize=(7, 4),
        layout="constrained",  # Alternative: tight_layout=True
        **kwargs,
    )

    # Use ETH colours for plots
    if isinstance(axes, np.ndarray):
        for ax in axes:
            ax.set_prop_cycle(
                cycler(
                    color=[
                        "#215CAF",  # ETH blue
                        "#B7352D",  # ETH red
                        "#627313",  # ETH green
                        "#A7117A",  # ETH purple
                        "#8E6713",  # ETH bronze
                        "#007894",  # ETH petrol
                        "#6F6F6F",  # ETH gray
                    ],
                )
            )
    return fig, axes


def style_axes(
    axes: Axes, nticks: int = 2, xunit: str = "", yunit: str = "", serif: bool = False
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


def _adjust_fonts(ax: Axes, serif: bool = False) -> None:
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
            ax.title,
            ax.xaxis.label,
            ax.yaxis.label,
            *ax.get_xticklabels(),
            *ax.get_yticklabels(),
            *(ax.get_legend().get_texts() if ax.get_legend() else ()),
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
        useOffset: Optional[bool | float] = None,
        useMathText: Optional[bool] = None,
        useLocale: Optional[bool] = None,
    ) -> None:
        super().__init__(useOffset, useMathText, useLocale)
        self.unit = unit

    def __call__(self, x: float, pos: Optional[int] = None) -> str:
        res = super().__call__(x, pos)
        if x == self.locs[-1]:
            res += self.unit
        return res
