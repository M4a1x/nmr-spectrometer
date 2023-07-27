#!/usr/bin/env python3

import logging
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.optimize as spo

from spectrometer import FID1D, PulseExperiment, PulseSequence, make_axes, style_axes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    # Send series of pulses with increasing length
    pulse_lengths_us = np.linspace(1, 100, 200)
    delay_us = 30
    repetition_time_s = 5
    sequences = [
        PulseSequence.simple(pulse_length_us=pulse_length_us, delay_us=delay_us)
        for pulse_length_us in pulse_lengths_us
    ]
    exp = PulseExperiment(tx_freq=25_090_230)
    datas = exp.send_sequences(
        sequences=sequences, rx_length_us=10e3, repetition_time_s=repetition_time_s
    )

    # Save FIDs
    fids: list[FID1D] = []
    for i, data in enumerate(datas):
        fid = FID1D(
            data=data,
            spectral_width=exp.sample_rate,
            carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
            observation_freq=exp.rx_freq,
            label="1H",
            sample="Water",
            pulse_file=f"one_of_repeated_90_degree_pulses,length={pulse_lengths_us[i]}us,delay={delay_us}us,repetition_time={repetition_time_s}s",
            spectrometer="magnETHical v0.1",
        )
        timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
        fid.to_file(
            f"data/{timestr}-{fid.sample}-{fid.label}/{timestr}-{fid.sample}-{fid.label}-{fid.pulse_file}.fid"
        )
        fids.append(fid)

    # Process
    signal_strengths = np.empty_like(pulse_lengths_us)
    for i, fid in enumerate(fids):
        x, y = fid.simple_fft(phase_shift_kwargs=False)
        y2 = np.abs(y) ** 2
        integral = np.trapz(x=x, y=y2)
        signal_strengths[i] = integral

    # Plot raw data
    fig, ax = make_axes()
    ax.plot(pulse_lengths_us, signal_strengths, linestyle="", marker=".")
    ax.set_title("Signal strength over pulse length")
    ax.set_xlabel("Pulse length")
    ax.set_ylabel("Signal strength")
    style_axes(
        ax,
        nticks=4,
        xunit="μs",
        yunit="au",
    )

    # Try to plot simple least squares fit
    try:
        fit = fit_decaying_squared_sinusoid(pulse_lengths_us, signal_strengths)
        pulse_lengths_us_fine = np.linspace(
            pulse_lengths_us[0], pulse_lengths_us[-1], len(pulse_lengths_us) * 10
        )
        ax.plot(pulse_lengths_us_fine, fit["function"](pulse_lengths_us_fine))
    except (RuntimeError, ValueError, spo.OptimizeWarning) as err:
        logger.warning("Couldn't estimate curve fitting: %s", str(err))

    # Save plot
    timestr = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    fig.savefig(
        f"data/{timestr}-{fid.sample}-{fid.label}/{timestr}-{fid.sample}-{fid.label}-rabi_nutation.pdf"
    )
    fig.show()
    plt.show(block=True)


def fit_decaying_squared_sinusoid(x: npt.NDArray, y: npt.NDArray) -> dict:
    """Fit a decaying squared sine wave to the input sequence

    f(x) = a * e^-lt * sin^2 (w * t + p) + c

    Returns:
        Fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    def decaying_sinusoid_squared(t, amplitude, lambda_, freq, phase, offset):
        return (
            amplitude * np.exp(-lambda_ * t) * np.sin(2 * np.pi * freq * t + phase) ** 2
            + offset
        )

    # Guess initial fitting parameters
    frequencies = np.fft.fftfreq(len(x), (x[1] - x[0]))  # assume uniform spacing
    fft = abs(np.fft.fft(y))
    # excluding the zero frequency "peak", which is related to offset
    guess_frequency = np.abs(frequencies[np.argmax(fft[1:]) + 1])
    guess_amplitude = np.std(y) * 2.0**0.5
    guess_offset = np.mean(y)
    guess_phase = 0
    guess_lambda = 0
    guess = (guess_amplitude, guess_lambda, guess_frequency, guess_phase, guess_offset)

    popt, _pcov = spo.curve_fit(decaying_sinusoid_squared, x, y, p0=guess)
    return {
        "amplitude": popt[0],
        "lambda": popt[1],
        "frequency": popt[2],
        "phase": popt[3],
        "offset": popt[4],
        "function": lambda t: decaying_sinusoid_squared(t, *popt),
    }


if __name__ == "__main__":
    main()
