from typing import Any, Self

import numpy as np
import numpy.typing as npt
import scipy.optimize as spo
from nmrglue.process.proc_base import ps


def decaying_sinusoid_squared(
    t: npt.NDArray,
    amplitude: float,
    lambda_: float,
    freq: float,
    phase: float,
    offset: float,
) -> npt.NDArray:
    return (
        amplitude
        * np.exp(-lambda_ * t)
        * np.square(np.sin(2 * np.pi * freq * t + phase))
        + offset
    )


def estimate_noise_amplitude(amplitudes: npt.NDArray, frm: int, to: int) -> float:
    """Estimate the noise of the spectrum

    This is done by averaging the absolute of the spectrum between two points
    that don't contain a peak

    Args:
        amplitudes (npt.NDArray): array of amplitudes of the spectrum in arbitrary units
        frm (int): Start of the average
        to (int): End of the average

    Returns:
        float: Average of the absolute noise
    """
    return np.average(np.abs(amplitudes[frm:to]))


def fit_exp_decay(x: npt.NDArray, y: npt.NDArray) -> dict:
    """Fit a decay exponential to the input sequence

    f(x) = amplitude * e^(-lambda*t) + offset

    Returns:
        Fitting parameters "amplitude", "lambda", "offset" and the resulting "function"
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    # Guess initial fitting parameters
    guess_amplitude = np.max(y) - np.min(y)
    guess_offset = np.min(y)
    guess_lambda = 0
    guess = (guess_amplitude, guess_lambda, guess_offset)

    popt, _pcov = spo.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
        exp_decay, x, y, p0=guess
    )
    return {
        "amplitude": popt[0],
        "lambda": popt[1],
        "offset": popt[2],
        "function": lambda t: exp_decay(t, *popt),
    }


class exp_decay:
    def __init__(self, amplitude: float, lambda_: float, offset: float) -> None:
        self.amplitude = amplitude
        self.lambda_ = lambda_
        self.offset = offset

    @staticmethod
    def function(
        t: npt.NDArray, amplitude: float, lambda_: float, offset: float
    ) -> npt.NDArray:
        return amplitude * np.exp(-lambda_ * t) + offset

    def __call__(self, t: float | npt.NDArray) -> float | npt.NDArray:
        return self.function(t, self.amplitude, self.lambda_, self.offset)

    @classmethod
    def fit(cls, x: npt.NDArray, y: npt.NDArray) -> Self:
        """Fit a decay exponential to the input sequence

        f(x) = amplitude * e^(-lambda*t) + offset

        Returns:
            Self
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        # Guess initial fitting parameters
        guess_amplitude = np.max(y) - np.min(y)
        guess_offset = np.min(y)
        guess_lambda = 0
        guess = (guess_amplitude, guess_lambda, guess_offset)

        popt, _pcov = spo.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
            cls.function, x, y, p0=guess
        )
        return cls(amplitude=popt[0], lambda_=popt[1], offset=popt[2])


class decaying_sinus:
    def __init__(
        self, amplitude: float, lambda_: float, freq: float, phase: float, offset: float
    ) -> None:
        self.amplitude = amplitude
        self.lambda_ = lambda_
        self.freq = freq
        self.phase = phase
        self.offset = offset

    @staticmethod
    def function(
        t: npt.NDArray,
        amplitude: float,
        lambda_: float,
        freq: float,
        phase: float,
        offset: float,
    ) -> npt.NDArray:
        return (
            amplitude * np.exp(-lambda_ * t) * np.sin(2 * np.pi * freq * t + phase)
            + offset
        )

    @property
    def period(self) -> float:
        return 1 / self.freq

    def __call__(self, t: float | npt.NDArray) -> float | npt.NDArray:
        return self.function(
            t, self.amplitude, self.lambda_, self.freq, self.phase, self.offset
        )

    @classmethod
    def fit(cls, x: npt.NDArray, y: npt.NDArray) -> Self:
        """Fit a decaying squared sine wave to the input sequence

        f(t) = a * e^-lt * sin(2 * pi * f * t + p) + c

        Returns:
            Fitting parameters "amplitude", "lambda", "frequency", "phase", "offset", and "function"
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        # Guess initial fitting parameters
        frequencies = np.fft.fftfreq(len(x), (x[1] - x[0]))  # assume uniform spacing
        fft = abs(np.fft.fft(y))
        # excluding the zero frequency "peak", which is related to offset
        guess_frequency = np.abs(frequencies[np.argmax(fft[1:]) + 1])
        guess_amplitude = np.std(y) * np.sqrt(2.0)
        guess_offset = np.mean(y)
        guess_phase = 0
        guess_lambda = 0
        guess = (
            guess_amplitude,
            guess_lambda,
            guess_frequency,
            guess_phase,
            guess_offset,
        )

        popt, _pcov = spo.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
            cls.function, x, y, p0=guess
        )
        return cls(
            amplitude=popt[0],
            lambda_=popt[1],
            freq=popt[2],
            phase=popt[3],
            offset=popt[4],
        )

    def __str__(self) -> str:
        return (
            f"Amplitude: {self.amplitude}\n"
            f"Frequency: {self.freq}\n"
            f"Phase: {self.phase}\n"
            f"Offset: {self.offset}\n"
            f"Lambda: {self.lambda_}"
        )


class lorentzian:
    def __init__(self, amplitude: float, gamma: float, position: float) -> None:
        self.amplitude = amplitude
        self.gamma = gamma
        self.position = position

    @staticmethod
    def function(
        x: npt.NDArray, position: float, gamma: float, amplitude: float
    ) -> npt.NDArray:
        return amplitude * (
            np.square(gamma) / (np.square(x - position) + np.square(gamma))
        )

    def __call__(self, x: npt.NDArray) -> Any:
        return self.function(x, self.position, self.gamma, self.amplitude)

    @classmethod
    def fit(cls, x: npt.NDArray, y: npt.NDArray) -> Self:
        """Fit a lorentzian function to the input sequence

        f(x) = amplitude * (gamma**2 / ((x - position)**2 + gamma**2))

        Returns:
            Fitting parameters "amplitude", "gamma", "position" and the resulting "function"
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        # Guess initial fitting parameters
        guess_amplitude = np.max(y) - np.min(y)
        guess_position = x[np.argmax(y)]

        def find_nearest_idx(array: npt.NDArray, value: float) -> float:
            return np.abs(array - value).argmin()

        guess_gamma = (
            x[
                len(y[np.argmax(y) :])
                + find_nearest_idx(y[np.argmax(y) :], guess_amplitude / 2)
            ]
            - x[find_nearest_idx(y[: np.argmax(y)], guess_amplitude / 2)]
        )
        guess = (guess_position, guess_gamma, guess_amplitude)

        popt, _pcov = spo.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
            cls.function, x, y, p0=guess
        )
        return cls(position=popt[0], gamma=np.abs(popt[1]), amplitude=popt[2])

    @property
    def fwhm(self) -> float:
        return self.gamma * 2

    def __str__(self) -> str:
        return (
            f"Amplitude: {self.amplitude}\n"
            f"Gamma: {self.gamma}\n"
            f"Full Width at Half Maximum: {self.fwhm}\n"
            f"Position: {self.position}"
        )


def fit_decaying_squared_sinusoid(x: npt.NDArray, y: npt.NDArray) -> dict:
    """Fit a decaying squared sine wave to the input sequence

    f(x) = a * e^-lt * sin^2 (w * t + p) + c

    Returns:
        Fitting parameters "amplitude", "lambda", "frequency", "phase", "offset", and "function"
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    # Guess initial fitting parameters
    frequencies = np.fft.fftfreq(len(x), (x[1] - x[0]))  # assume uniform spacing
    fft = abs(np.fft.fft(y))
    # excluding the zero frequency "peak", which is related to offset
    guess_frequency = np.abs(frequencies[np.argmax(fft[1:]) + 1])
    guess_amplitude = np.std(y) * np.sqrt(2.0)
    guess_offset = np.min(y)
    guess_phase = 0
    guess_lambda = 0
    guess = (guess_amplitude, guess_lambda, guess_frequency, guess_phase, guess_offset)

    popt, _pcov = spo.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
        decaying_sinusoid_squared, x, y, p0=guess
    )
    return {
        "amplitude": popt[0],
        "lambda": popt[1],
        "frequency": popt[2],
        "phase": popt[3],
        "offset": popt[4],
        "function": lambda t: decaying_sinusoid_squared(t, *popt),
    }


def find_phase_shift(
    data: npt.NDArray, p0_start: float = 0, peak_width: float = 100
) -> float:
    """Find a zero order phase shift that minimizes the minima around the peak

    Args:
        data (npt.NDArray): Spectral data (i.e. y-values) containing peaks
        p0_start (float, optional): Offset to start optimizing from. Defaults to 0.

    Returns:
        float: Zero order phase shift that minimizes the minima around the peak
    """

    (p0,) = spo.fmin(
        _phase_shift_score, x0=p0_start, args=(data, peak_width), disp=False
    )
    return p0


def _phase_shift_score(p0: float, data: npt.NDArray, peak_width: float) -> float:
    """Shift `data` by zero order phase of `p0` and return the absolute difference between the
    two minima surrounding the highest peak. This can be used for scoring how good the provided
    phase shift `p0` is

    Args:
        p0 (float): Zero order phase shift in degrees
        data (npt.NDArray): Spectral data (i.e. y-values) containing at least one peak
        peak_width (float): Width around the highest peak to look for minima in

    Returns:
        float: Absolute difference between the two minima surrounding the highest peak
    """
    data = ps(data, p0=p0).real

    max_idx = np.argmax(data)
    left_minimum = np.min(data[max_idx - peak_width : max_idx])
    right_minimum = np.min(data[max_idx : max_idx + peak_width])

    return np.abs(left_minimum - right_minimum)
