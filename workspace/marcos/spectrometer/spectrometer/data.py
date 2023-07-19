import copy
import io
import logging
from pathlib import Path
from typing import Optional, Self, Tuple

import matplotlib as mpl
import nmrglue as ng
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from spectrometer.plot import make_axes, style_axes

logger = logging.getLogger(__name__)

# TODO: Write processed (spectral) data as *.ft1 (number indicates last processed dimension)


class FID1D:
    """Class representing 1D Free Induction Decay (FID) data and metadata

    Metadata is internally stored in a dictionary (`self._pipedic`) in NMRPipe format using nmrglue.
    This is an implementation detail and should not be relied upon! Convenience methods for
    conversion of nmrglue data are supplied `_from_udic` and `_from_pipe` as well as getting back
    the respective dictionaries (`self._udic` and `self._pipedic`). Using the public
    interface is strongly preferred, though as this might change at any time!
    """

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
        self._udic = universal_dict
        self.data = data

    @property
    def _udic(self) -> dict:
        return ng.pipe.guess_udic(self._pipedic, self.data)

    @_udic.setter
    def _udic(self, universal_dict: dict) -> None:
        if not isinstance(universal_dict, dict) or "ndim" not in universal_dict.keys():
            msg = "Not a universal_dictionary!"
            raise ValueError(msg)
        if universal_dict["ndim"] > 1 or 1 in universal_dict.keys():
            msg = "Only 1D FIDs supported!"
            raise ValueError(msg)
        if not universal_dict[0]["time"] or universal_dict[0]["freq"]:
            msg = "Only time domain signals supported!"
            raise ValueError(msg)
        self._pipedic = ng.pipe.create_dic(universal_dict)

    @property
    def label(self) -> str:
        return self._udic[0]["label"]

    @property
    def carrier_freq(self) -> float:
        return self._udic[0]["car"]

    @property
    def observation_freq(self) -> float:
        return self._udic[0]["obs"] * 1e6

    @property
    def size(self) -> float:
        return self.data.shape[0]

    @property
    def spectral_width(self) -> float:
        return self._udic[0]["sw"]

    @classmethod
    def _from_udic(cls: Self, universal_dict: dict, data: npt.NDArray) -> Self:
        """Convenience method to create an FID from a nmrglue universal_dictionary

        Args:
            universal_dict (dict): nmrglue universal_dictionary `udic`
            data (npt.NDArray): FID time domain data

        Returns:
            Self: New FID1D instance
        """
        fid = cls(
            data,
            spectral_width=universal_dict[0]["sw"],
            carrier_freq=universal_dict[0]["car"],
            label=universal_dict[0]["label"],
            observation_freq=universal_dict[0]["obs"] * 1e6,
        )
        if fid.size != universal_dict[0]["size"]:
            msg = "Size length mismatch between universal_dict metadata and actual data"
            raise ValueError(msg)

        fid_udic = fid._udic
        fid_udic.update(universal_dict)
        fid._udic = fid_udic
        return fid

    @classmethod
    def _from_pipe(cls: Self, pipe_dict: dict, data: npt.NDArray) -> Self:
        """Convenience method to create an FID from an nmrglue pipe dictionary

        Args:
            pipe_dict (dict): dictionary with NMRPipe metadata as give by nmrglue
            data (npt.NDArray): 1D time domain NMR FID data

        Returns:
            Self: New FID1D instance
        """
        fid = cls._from_udic(ng.pipe.guess_udic(pipe_dict, data), data)
        fid_pipedic = fid._pipedic
        fid_pipedic.update(pipe_dict)
        fid._pipedic = fid_pipedic
        return fid

    @classmethod
    def from_file(cls: Self, file: Path | str | io.BytesIO) -> Self:
        """Create a FID1D instance from an NMRPipe file containing 1D time domain data

        Args:
            file (Path | str | io.BytesIO): Location of the NMRPipe formatted data. Path, string and
            in memory buffer are supported

        Returns:
            Self: New FID1D instance
        """
        dic, data = ng.pipe.read(filename=file)
        return cls._from_pipe(dic, data)

    def to_file(self, file: Path | str | io.BytesIO) -> None:
        """Store the 1D FID time domain data in a file in NMRPipe format

        Args:
            file (Path | str | io.BytesIO): Location to write to. Path, string and in memory buffers
            are supported

        Raises:
            ValueError: On invalid file name. NMRPipe files must end in `.fid`
        """
        if (isinstance(file, (str, Path))) and Path(file).suffix != ".fid":
            msg = f"Time domain data files have to end in '.fid'. Invalid filename: {file!s}"
            raise ValueError(msg)
        self._pipedic["FDPIPEFLAG"] = 1.0  # Set NMRPipe data stream header
        ng.pipe.write(file, self._pipedic, self.data, overwrite=False)

    def show_plot(self) -> None:
        fig = self._plot()
        fig.show()

    def save_plot(self, file: Path | str | io.BytesIO) -> None:
        fig = self._plot()
        fig.savefig(file)

    def _plot(self, us_scale: bool = False, serif: bool = False) -> Figure:
        fig, axes = make_axes(rows=1, columns=1)
        uc = ng.pipe.make_uc(self._pipedic, self.data)
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

    def show_simple_fft(self) -> None:
        fig = self._plot_simple_fft()
        fig.show()

    def save_simple_fft(self, file: Path | str | io.BytesIO) -> None:
        fig = self._plot_simple_fft()
        fig.savefig(file)

    def simple_fft(self) -> tuple[dict, npt.NDArray]:
        dic, data = copy.deepcopy(self._pipedic), copy.deepcopy(self.data)
        dic, data = ng.pipe_proc.sp(dic, data)  # Sine bell apodization
        dic, data = ng.pipe_proc.zf(dic, data, auto=True)  # Zero fill
        dic, data = ng.pipe_proc.ft(dic, data, auto=True)  # Complex Fourier transform
        data = ng.proc_autophase.autops(data, fn="acme")  # Auto phase shift
        dic, data = ng.pipe_proc.di(dic, data)  # Delete imaginaries
        return dic, data

    def _plot_simple_fft(self, hz_scale: bool = True, serif: bool = False) -> Figure:
        dic, data = self.simple_fft()
        fig, axes = make_axes(rows=1, columns=1)
        uc = ng.pipe.make_uc(dic, data)
        axes.plot(uc.hz_scale() if hz_scale else uc.ppm_scale(), data)
        axes.set_title(f"Spectrum of {self.label}")
        axes.set_xlabel("Frequency")
        axes.set_ylabel("Amplitude")
        style_axes(
            axes,
            nticks=4,
            xunit="Hz" if hz_scale else "ppm",
            yunit="au",
            serif=serif,
        )
        return fig

        # freq_fft = np.fft.fftshift(np.fft.fftfreq(n=len(data), d=sample_time_us / 1e6))
