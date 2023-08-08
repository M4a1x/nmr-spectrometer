#!/usr/bin/env python3

import logging
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.optimize as spo

from spectrometer import FID1D, NMRSequence, Spectrometer, make_axes, style_axes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    # Perform multiple spin echoes with increasing delay
    delays_us = np.linspace(100, 300, 100)
    pulse_length_us = 9
    repetition_time_s = 5
    sequences = [
        NMRSequence.spin_echo(
            pulse_length_us=pulse_length_us,
            delay_tau_us=delay_us,
            delay_after_p2_us=30,
            record_length_us=10_000,
        )
        for delay_us in delays_us
    ]
    exp = Spectrometer(tx_freq=25_090_230)
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
            pulse_file=f"one_of_repeated_spin_echoes,length={pulse_length_us}us,delay={delays_us[i]}us,repetition_time={repetition_time_s}s",
            spectrometer="magnETHical v0.1",
        )
        timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
        fid.to_file(
            f"data/{timestr}-{fid.sample}-{fid.label}-t2-decay/{timestr}-{fid.sample}-{fid.label}-{fid.pulse_file}.fid"
        )
        fids.append(fid)

    # Process
    signal_strengths = np.empty_like(delays_us)
    for i, fid in enumerate(fids):
        x, y = fid.simple_fft(phase_shift_kwargs=False)
        y2 = np.abs(y) ** 2
        integral = np.trapz(x=x, y=y2)
        signal_strengths[i] = integral

    # Plot raw data
    fig, ax = make_axes()
    ax.plot(delays_us, signal_strengths, linestyle="", marker=".")
    ax.set_title("Signal strength over delay")
    ax.set_xlabel("Delay")
    ax.set_ylabel("Signal strength")
    style_axes(
        ax,
        nticks=4,
        xunit="μs",
        yunit="au",
    )

    # Try to plot simple least squares fit
    try:
        fit = fit_decay(delays_us, signal_strengths)
        pulse_lengths_us_fine = np.linspace(
            delays_us[0], delays_us[-1], len(delays_us) * 10
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


def fit_decay(x: npt.NDArray, y: npt.NDArray) -> dict:
    """Fit a decay exponential to the input sequence

    f(x) = amplitude * e^(-lambda*t) + offset

    Returns:
        Fitting parameters "amplitude", "lambda", "offset" and the resulting "function"
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    def decay(t, amplitude, lambda_, offset):
        return amplitude * np.exp(-lambda_ * t) + offset

    # Guess initial fitting parameters
    guess_amplitude = np.max(y) - np.min(y)
    guess_offset = np.min(y)
    guess_lambda = 0
    guess = (guess_amplitude, guess_lambda, guess_offset)

    popt, _pcov = spo.curve_fit(decay, x, y, p0=guess)
    return {
        "amplitude": popt[0],
        "lambda": popt[1],
        "offset": popt[2],
        "function": lambda t: decay(t, *popt),
    }


if __name__ == "__main__":
    main()
