import logging
import io
import nmrglue as ng
import numpy as np
import numpy.typing as npt
from pathlib import Path
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Self, Tuple, Optional
from matplotlib import ticker

from .plot import make_axes, style_axes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Write processed (spectral) data as *.ft1 (number indicates last processed dimension)


class FID1D:
    def __init__(
        self,
        raw_data: npt.NDArray,
        spectral_width: float,  # Sampling Bandwidth
        carrier_freq: float,  # Offset freq between observation_freq and resonant_freq (depends on magnet)
        label: str = "1H",  # or "C","N",... for other nuclei
        observation_freq: float = 25e6,  # assuming downsampling freq and pulse freq to be equal
    ) -> None:
        """Create new container from time domain data"""
        data = np.asarray(raw_data, dtype=np.complex64)

        if not data.ndim == 1:
            msg = "Time domain data must be an array of one dimension"
            raise ValueError(msg)

        if not np.any(np.iscomplex(data)):
            msg = "The input data doesn't seem to consist of complex numbers"
            raise ValueError(msg)

        universal_dict = ng.fileio.fileiobase.create_blank_udic(1)
        axis_dict = {
            "car": carrier_freq,
            "complex": True,
            "encoding": "direct",  # 1D => direct dimension. Use "states" for all indirect dimensions
            "freq": False,  # Time domain data
            "time": True,
            "label": label,
            "obs": observation_freq / 1e6,
            "size": data.shape[0],
            "sw": spectral_width,
        }
        universal_dict = {
            "ndim": 1,
            0: axis_dict,
        }

        self.params = ng.pipe.create_dic(universal_dict)
        self.data = data

    @property
    def label(self) -> str:
        return ng.pipe.guess_udic(self.params, self.data)[0]["label"]

    @property
    def carrier_freq(self) -> float:
        return ng.pipe.guess_udic(self.params, self.data)[0]["car"]

    @property
    def observation_freq(self) -> float:
        return ng.pipe.guess_udic(self.params, self.data)[0]["obs"] * 1e6

    @property
    def size(self) -> float:
        return self.data.shape[0]

    @property
    def spectral_width(self) -> float:
        return ng.pipe.guess_udic(self.params, self.data)[0]["sw"]

    @classmethod
    def from_file(cls: Self, file: Path) -> Self:
        if file.suffix != ".fid":
            logger.warning(
                "File %s doesn't end with '.fid'. Trying to load as NMRPipe file anyway...",
                str(file),
            )
        parameters, data = ng.pipe.read(filename=file)

        # TODO: check if time domain data (see parameters dic)
        cls(data, **parameters)

    def to_file(self, file: Path) -> None:
        if file.suffix != ".fid":
            msg = f"Time domain data files have to end in '.fid'. Invalid filename: {str(file)}"
            raise ValueError(msg)
        self.params["FDPIPEFLAG"] = 1.0  # Set NMRPipe data stream header
        ng.pipe.write(str(file.resolve()), self.params, self.data, overwrite=False)

    def show_plot(self) -> None:
        fig = self._plot()
        fig.show()

    def save_plot(self, file: Path) -> None:
        fig = self._plot()
        fig.savefig(file)

    def _plot(self, us_scale: bool = False, serif: bool = False) -> Figure:
        fig, axes = make_axes(rows=1, columns=1)
        uc = ng.pipe.make_uc(self.params, self.data)
        axes.plot(uc.us_scale() if us_scale else uc.ms_scale(), self.data)
        axes.set_title(f"FID of {self.label}")
        axes.set_ylabel("Amplitude")
        axes.set_xlabel("Time")
        style_axes(
            axes,
            nticks=4,
            xunit="μs" if us_scale else "ms",
            yunit="au",
            serif=serif,
        )
        return fig
