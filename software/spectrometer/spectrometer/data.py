import copy
import datetime as dt
import io
import logging
from pathlib import Path
from typing import Self

import nmrglue as ng
import numpy as np
import numpy.typing as npt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from spectrometer.process import auto_find_phase_shift
from spectrometer import plot

logger = logging.getLogger(__name__)
NMRPIPE_MAX_LABEL_LENGTH = 8
NMRPIPE_MAX_OPERNAME_LENGTH = 32
NMRPIPE_MAX_TITLE_LENGTH = 60
NMRPIPE_MAX_COMMENT_LENGTH = 160


class FID1D:
    """Class representing 1D Free Induction Decay (FID) data and metadata of an NMR experiment

    Convenience methods for conversion of `nmrglue` data are supplied `_from_udic` and `_from_pipe`,
    as well as getting back the respective dictionaries (`self._get_udic` and `self._get_pipedic`).
    Using the public interface is strongly preferred, though as this might change at any time!

    This class is intended as a simple and in scope restricted helper for working with a time domain
    FID measurement. If constructed through __init__() it is guaranteed to be writable as a *.fid
    file and to be read in again without any loss of information (see test suite).
    """

    def __init__(
        self,
        data: npt.ArrayLike,
        spectral_width: float,
        carrier_freq: float,
        observation_freq: float,
        label: str,
        sample: str,
        pulse: str | Path,
        spectrometer: str,
        timestamp: dt.datetime | None = None,
    ) -> None:
        """Create new simple 1D FID container from time domain data

        Args:
            data (npt.NDArray): 1D complex (i.e. after QI-Demodulation time domain data)
            spectral_width (float): Sampling Bandwidth (inverse of dwell time)
            carrier_freq (float): Offset freq between observation_freq and resonant_freq
            (depends on magnet)
            observation_freq (float): Assuming downsampling freq and pulse freq to be equal
            label (str): Usually "1H", "13C", "N", ... (8 chars max)
            sample (str): Sample description (Water, Acteone, Methanol, Benzene,
            Trifluortoluol, ...) (60 chars max)
            pulse (str | Path): Name of the file describing the used pulse sequence for this
            FID, or a description of the pulse sequence (160 chars max)
            spectrometer (str): Name of the spectrometer used for capturing the FID, 32 chars max
            timestamp (datetime.datetime, optional): Time of the experiment in UTC. Defaults to
            datetime.datetime.now(tz=datetime.UTC)

        Raises:
            ValueError: On invalid argument value. e.g. dimension mismatch, invalid char length, ...
        """
        data = np.asarray(data, dtype=np.complex64)

        if not data.ndim == 1:
            msg = "Time domain data must be an array of one dimension"
            raise ValueError(msg)

        if not np.any(np.iscomplex(data)):
            msg = "The input data doesn't seem to consist of complex numbers"
            raise ValueError(msg)

        if len(str(pulse)) > NMRPIPE_MAX_COMMENT_LENGTH:
            msg = f"Length of pulse file name '{pulse}' is longer than 160 characters"
            raise ValueError(msg)

        if len(spectrometer) > NMRPIPE_MAX_OPERNAME_LENGTH:
            msg = f"Name of spectrometer '{spectrometer}' is longer than 32 characters"
            raise ValueError(msg)

        if len(sample) > NMRPIPE_MAX_TITLE_LENGTH:
            msg = f"Sample description '{sample}' is longer than 60 characters"
            raise ValueError(msg)

        if len(label) > NMRPIPE_MAX_LABEL_LENGTH:
            msg = f"Label '{label}' is longer than 8 characters"
            raise ValueError(msg)

        self.carrier_freq = carrier_freq
        self.label = label
        self.observation_freq = observation_freq
        self.spectral_width = spectral_width
        self.sample = sample
        self.pulse = pulse
        self.spectrometer = spectrometer
        self.timestamp = (
            timestamp
            if timestamp
            else dt.datetime.now(tz=dt.UTC).replace(microsecond=0)
        )

        self.data = data

    @property
    def size(self) -> int:
        """Number of elements in the data array

        Returns:
            float: Length of the time domain data
        """
        return self.data.shape[0]

    @property
    def us_scale(self) -> npt.NDArray:
        uc = ng.pipe.make_uc(self._get_pipedic(), self.data)
        return uc.us_scale()

    @property
    def ms_scale(self) -> npt.NDArray:
        uc = ng.pipe.make_uc(self._get_pipedic(), self.data)
        return uc.ms_scale()

    def _get_udic(self) -> dict:
        """Generate a `nmrglue` universal_dictionary

        This drops all in formation about the pulse sequence as well as the sample. Only the basic
        information is present in a `universal_dictionary`. See the `nmrglue` documentation
        at https://nmrglue.readthedocs.io/en/latest/tutorial.html#universal-dictionaries for details.

        The resulting dictionary contains one dictionary per dimension (i.e. here only one) with the keys:
        "car" -> carrier frequency, offset between observation_freq and resonant_freq (depends on magnet)
        "complex" -> True for complex data, False for magnitude only
        "encoding" -> "direct" for the direct dimension, "states" for indirect (see `nmrglue` docs for others)
        "freq" -> True for frequency domain data, false otherwise
        "time" -> True for time domain data, false otherwise
        "label" -> Label of the dimension, usually the nuclei, e.g. 13C, 1H, ...
        "obs" -> observation frequency (central freq of the spectrum/downconversion frequency) in MHz
        "size" -> length of the time domain data array, i.e. `self.data`
        "sw" -> Sampling frequency in Hertz, inverse of the dwell time/sampling time

        Returns:
            dict: `nmrglue` `universal_dictionary`
        """
        universal_dict = ng.fileio.fileiobase.create_blank_udic(1)
        direct_dim_dict = universal_dict[0]
        direct_dim_dict.update(
            {
                "car": self.carrier_freq,
                "complex": True,
                "encoding": "direct",  # 1D => direct dimension. Use "states" for all indirect dimensions
                "freq": False,  # Time domain data
                "time": True,
                "label": self.label,
                "obs": self.observation_freq / 1e6,
                "size": self.data.shape[0],
                "sw": self.spectral_width,
            }
        )

        universal_dict.update(
            {
                "ndim": 1,
                0: direct_dim_dict,
            }
        )
        return universal_dict

    def _get_pipedic(self) -> dict:
        pipedic = ng.pipe.create_empty_dic()
        pipedic["FDDIMCOUNT"] = 1.0
        pipedic["FDDIMORDER"] = [2.0, 1.0, 3.0, 4.0]
        pipedic["FDSIZE"] = self.size
        pipedic["FDREALSIZE"] = self.size
        pipedic["FD2DPHASE"] = 0.0

        pipedic["FDTITLE"] = self.sample
        pipedic["FDCOMMENT"] = str(self.pulse)
        pipedic["FDOPERNAME"] = self.spectrometer

        pipedic["FDYEAR"] = self.timestamp.year
        pipedic["FDMONTH"] = self.timestamp.month
        pipedic["FDDAY"] = self.timestamp.day
        pipedic["FDHOURS"] = self.timestamp.hour
        pipedic["FDMINS"] = self.timestamp.minute
        pipedic["FDSECS"] = self.timestamp.second

        axis_prefix = "FDF2"
        pipedic[f"{axis_prefix}SW"] = self.spectral_width
        pipedic[f"{axis_prefix}OBS"] = self.observation_freq / 1e6
        pipedic[f"{axis_prefix}CAR"] = self.carrier_freq / pipedic[f"{axis_prefix}OBS"]
        pipedic[f"{axis_prefix}LABEL"] = self.label
        pipedic[f"{axis_prefix}QUADFLAG"] = 0.0  # complex data
        pipedic[f"{axis_prefix}FTFLAG"] = 0.0
        pipedic[f"{axis_prefix}TDSIZE"] = self.size
        pipedic[f"{axis_prefix}APOD"] = pipedic[f"{axis_prefix}TDSIZE"]
        pipedic[f"{axis_prefix}CENTER"] = int(self.size / 2) + 1

        # Origin (last point) is CAR*OBS-SW*(N/2-1)/N
        # see Fig 3.1 on p.36 of Hoch and Stern and nmrglue.pipe.add_axis_to_dic
        pipedic[f"{axis_prefix}ORIG"] = (
            pipedic[f"{axis_prefix}CAR"] * pipedic[f"{axis_prefix}OBS"]
            - pipedic[f"{axis_prefix}SW"]
            * (self.size - pipedic[f"{axis_prefix}CENTER"])
            / self.size
        )

        return pipedic

    @classmethod
    def _from_udic(cls: Self, universal_dict: dict, data: npt.NDArray) -> Self:
        """Convenience method to create a 1D FID from a nmrglue universal_dictionary and corresponding
        time domain data array

        Args:
            universal_dict (dict): `nmrglue` universal_dictionary `udic`
            data (npt.NDArray): FID time domain data `data`

        Returns:
            Self: New FID1D instance
        """
        if not isinstance(universal_dict, dict) or "ndim" not in universal_dict.keys():
            msg = "Not a universal_dictionary!"
            raise ValueError(msg)
        if universal_dict["ndim"] > 1 or 1 in universal_dict.keys():
            msg = "Only 1D FIDs supported!"
            raise ValueError(msg)
        if not universal_dict[0]["time"] or universal_dict[0]["freq"]:
            msg = "Only time domain signals are supported!"
            raise ValueError(msg)
        if len(data) != universal_dict[0]["size"]:
            msg = "Size length mismatch between universal_dict metadata and actual data"
            raise ValueError(msg)

        return cls(
            data=data,
            spectral_width=universal_dict[0]["sw"],
            carrier_freq=universal_dict[0]["car"],
            label=universal_dict[0]["label"],
            observation_freq=universal_dict[0]["obs"] * 1e6,
            sample="",
            pulse="",
            spectrometer="",
        )

    @classmethod
    def _from_pipe(cls: Self, pipe_dict: dict, data: npt.NDArray) -> Self:
        """Convenience method to create a 1D FID from an nmrglue pipe dictionary and corresponding
        time domain data array

        For "FDTITLE", "FDOPERNAME" and "FDCOMMENT" the file is assumed to have been written by
        this class and thus contain "Sample Description, "Spectrometer Name" and "Pulse Sequence File
        Name" respectively.

        Args:
            pipe_dict (dict): dictionary with NMRPipe metadata as given by nmrglue
            data (npt.NDArray): 1D time domain NMR FID data

        Returns:
            Self: New FID1D instance
        """
        if data.ndim != 1 or pipe_dict["FDDIMCOUNT"] != 1:
            msg = "Only 1D FIDs supported!"
            raise ValueError(msg)

        axis_num = int(pipe_dict["FDDIMORDER"][0])  # 1D data only
        axis_prefix = f"FDF{axis_num}"

        if pipe_dict["FDSIZE"] != pipe_dict["FDREALSIZE"] != f"{axis_prefix}TDSIZE":
            msg = "Data inconsistency in NMRPipe metadata and data array"
            raise ValueError(msg)

        if pipe_dict[f"{axis_prefix}QUADFLAG"] != 0:
            msg = "Only complex NMRPipe data is supported"
            raise ValueError(msg)

        if pipe_dict[f"{axis_prefix}FTFLAG"] != 0:
            msg = "Only time domain data is supported"
            raise ValueError(msg)

        return cls(
            data=data,
            spectral_width=pipe_dict[f"{axis_prefix}SW"],
            carrier_freq=pipe_dict[f"{axis_prefix}CAR"]
            * pipe_dict[f"{axis_prefix}OBS"],  # ppm -> Hz
            label=pipe_dict[f"{axis_prefix}LABEL"],
            observation_freq=pipe_dict[f"{axis_prefix}OBS"] * 1e6,
            sample=pipe_dict["FDTITLE"],
            pulse=pipe_dict["FDCOMMENT"],
            spectrometer=pipe_dict["FDOPERNAME"],
            timestamp=dt.datetime(
                year=int(pipe_dict["FDYEAR"]),
                month=int(pipe_dict["FDMONTH"]),
                day=int(pipe_dict["FDDAY"]),
                hour=int(pipe_dict["FDHOURS"]),
                minute=int(pipe_dict["FDMINS"]),
                second=int(pipe_dict["FDSECS"]),
                tzinfo=dt.UTC,  # Assuming UTC time
            ),
        )

    @classmethod
    def from_file(cls: Self, file: Path | str) -> Self:
        """Create a FID1D instance from an NMRPipe file containing 1D time domain data

        Args:
            file (Path | str): Location of the NMRPipe formatted data

        Returns:
            Self: New FID1D instance
        """
        dic, data = ng.pipe.read(filename=file)
        return cls._from_pipe(dic, data)

    def to_file(self, file: Path | str) -> None:
        """Store the 1D FID time domain data in a file in NMRPipe format

        If the filename doesn't end in *.fid, this will automatically append the correct suffix.
        Will never overwrite. A new file with an increasing counter will be created if a name
        conflict occurs.

        Args:
            file (Path | str): Location to write to

        Raises:
            ValueError: On invalid file name
        """
        file = Path(file)
        if file.suffix != ".fid":
            file = Path(f"{file}.fid")
        if file.exists():
            i = 1
            file_candidate = file
            while file_candidate.exists():
                file_candidate = Path(file.parent / f"{file.stem}{i}{file.suffix}")
                i += 1
            file = file_candidate
        ng.pipe.write(str(file.resolve()), self._get_pipedic(), self.data)

    def plot(self, *, us_scale: bool = False) -> Figure:
        fig, axes = plot.subplots(figsize=(10,5))
        uc = ng.pipe.make_uc(self._get_pipedic(), self.data)
        axes.plot(
            uc.us_scale() if us_scale else uc.ms_scale(),
            self.data.real,
            linestyle="",
            marker="o",
            markersize=0.8,
        )
        axes.set_title(f"FID of {self.label}")
        axes.set_ylabel("Amplitude [a.u.]")
        axes.set_xlabel(f"Time [{'μs' if us_scale else 'ms'}]")
        plot.format_axes(axes, font="Merriweather Sans")
        return fig

    def simple_fft(
        self,
        zero_fill_kwargs: dict | bool | None = None,
        fourier_transform_kwargs: dict | bool | None = None,
        phase_shift_kwargs: dict | bool | None = None,
        *,
        hz_scale: bool = True,
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """Very simple processing of the time domain data to obtain a frequency spectrum

        Without arguments this function will do an automatic zero fill, an automatic complex fourier
        transform and an automated phase correction (using 'ACME' algorithm by Chen Li et al. (JMR 2002)).

        Instead of relying on the automation algorithms, arguments to the individual functions can be
        passed in as dictionaries containing the keyword arguments for the functions. For a detailed
        description of the possible arguments see the `nmrglue` documentation for `nmrglue.pipe_proc.zf`,
        `nmrglue.pipe_proc.ft` and `nmrglue.pipe_proc.ps`

        For anything more complex a separate post processing is recommended.

        A respective processing step can be disabled by passing `False` instead of a kwargs dictionary.

        Args:
            zero_fill_kwargs (dict | bool, optional): Arguments for `nmrglue.pipe_proc.zf`. Defaults to None.
            fourier_transform_kwargs (dict | bool, optional): Arguments for `nmrglue.pipe_proc.ft`. Defaults to None.
            phase_shift_kwargs (dict | bool, optional): Arguments for `nmrglue.pipe_proc.ps`. Defaults to None.
            hz_scale (bool, optional): Scale of the 0-dimension. Pass 'True' for Hz scale, 'False'
            for ppm scale. Defaults to True.

        Returns:
            tuple[npt.NDArray, npt.NDArray]: Tuple of two 1D `numpy` arrays, the first representing the
            frequency bins and the second representing the complex fourier transform data.
        """
        # Make independent deep copy
        dic, data = copy.deepcopy(self._get_pipedic()), copy.deepcopy(self.data)

        # Zero fill
        if zero_fill_kwargs:
            dic, data = ng.pipe_proc.zf(dic, data, **zero_fill_kwargs)
        elif zero_fill_kwargs is None:
            dic, data = ng.pipe_proc.zf(dic, data, auto=True)
        else:
            pass  # Don't zero fill if passed 'False'

        # Complex Fourier Transform
        if fourier_transform_kwargs:
            dic, data = ng.pipe_proc.ft(dic, data, **fourier_transform_kwargs)
        elif fourier_transform_kwargs is None:
            dic, data = ng.pipe_proc.ft(dic, data)
        else:
            pass  # Don't fourier transform if passed 'False'

        # Phase Shift
        if phase_shift_kwargs:
            dic, data = ng.pipe_proc.ps(dic, data, **phase_shift_kwargs)
        elif phase_shift_kwargs is None:
            p0 = auto_find_phase_shift(data)
            dic, data = ng.pipe_proc.ps(dic, data, p0=p0)
        else:
            pass  # Don't shift if passed 'False'

        unit_converter = ng.pipe.make_uc(dic, data)
        scale = unit_converter.hz_scale() if hz_scale else unit_converter.ppm_scale()
        if phase_shift_kwargs is None:
            return scale, data, p0
        else:
            return scale, data

    def plot_simple_fft(self, *, hz_scale: bool = True, **kwargs) -> Figure:
        fig, axes = plot.subplots(figsize=(10,5))
        scale, data, _ = self.simple_fft(**kwargs, hz_scale=hz_scale)
        axes.plot(
            scale,
            data.real,
            linestyle="",
            marker="o",
            markersize=0.8,
        )
        axes.set_title(f"Spectrum of {self.label}")
        axes.set_xlabel("Frequency [Hz]")
        axes.set_ylabel("Amplitude [a.u.]")
        plot.format_axes(axes, font="Merriweather Sans")
        return fig

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FID1D):
            return (
                self.carrier_freq == other.carrier_freq
                and self.label == other.label
                and self.observation_freq == other.observation_freq
                and self.spectral_width == other.spectral_width
                and self.sample == other.sample
                and self.pulse == other.pulse
                and self.spectrometer == other.spectrometer
                and self.timestamp == other.timestamp
                and np.allclose(self.data, other.data)
            )
        else:
            return NotImplemented
