#!/usr/bin/env python3

import logging
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.optimize as spo

from spectrometer.plot import make_axes, style_axes
from spectrometer.pulse import send_varying_pulses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    freq = 25_090_230
    shortest_pulse_us = 1
    longest_pulse_us = 100
    num_samples = 200

    pulse_lengths_us = np.linspace(shortest_pulse_us, longest_pulse_us, num_samples)
    peaks = send_varying_pulses(
        pulse_lengths_us,
        pulse_delay_s=30,
        rx_delay_us=30,
        rx_length_us=10_000,
        freq=freq,
    )

    # Plot
    fig, ax = make_axes()
    ax.plot(pulse_lengths_us, peaks, linestyle="", marker=".")
    try:
        guess = fit_sin(pulse_lengths_us, peaks)
        pulse_lengths_us_fine = np.linspace(
            shortest_pulse_us, longest_pulse_us, num_samples * 10
        )
        ax.plot(pulse_lengths_us_fine, guess["fitfunc"](pulse_lengths_us_fine))
    except RuntimeError as err:
        logger.warning("Couldn't estimate sine curve fitting: %s", str(err))
    ax.set_title("Absolute peak sizes over pulse length")
    ax.set_xlabel("Pulse Length")
    ax.set_ylabel("Amplitude")
    style_axes(
        ax,
        nticks=4,
        xunit="μs",
        yunit="au",
    )
    timestr = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    fig.savefig(f"{timestr}-max_amplitude_vs_pulse_length_30s_delay.pdf")
    fig.show()

    plt.show(block=True)


def fit_sin(x: npt.NDArray, y: npt.NDArray) -> dict:
    """Fit a sinewave to the input sequence

    Returns:
        Fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"
    """
    x = np.asarray(x)
    y = np.asarray(y)
    ff = np.fft.fftfreq(len(x), (x[1] - x[0]))  # assume uniform spacing
    Fyy = abs(np.fft.fft(y))
    guess_freq = np.abs(
        ff[np.argmax(Fyy[1:]) + 1]
    )  # excluding the zero frequency "peak", which is related to offset
    guess_amp = np.std(y) * 2.0**0.5
    guess_offset = np.mean(y)
    guess = np.array([guess_amp, 2.0 * np.pi * guess_freq, 0.0, guess_offset])

    def sinfunc(t, A, w, p, c):
        return A * np.sin(w * t + p) + c

    popt, pcov = spo.curve_fit(sinfunc, x, y, p0=guess)
    A, w, p, c = popt
    f = w / (2.0 * np.pi)

    def fitfunc(t):
        return A * np.sin(w * t + p) + c

    return {
        "amp": A,
        "omega": w,
        "phase": p,
        "offset": c,
        "freq": f,
        "period": 1.0 / f,
        "fitfunc": fitfunc,
        "maxcov": np.max(pcov),
        "rawres": (guess, popt, pcov),
    }


if __name__ == "__main__":
    main()
