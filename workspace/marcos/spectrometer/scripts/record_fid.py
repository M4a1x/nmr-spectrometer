#!/usr/bin/env python3

import logging

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.optimize as spo
import scipy.signal as sps

from spectrometer import FID1D, PulseExperiment, PulseSequence, make_axes, style_axes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    pulse_length_us = 9
    delay_us = 25
    seq = PulseSequence.simple(
        pulse_length_us=pulse_length_us, delay_us=delay_us
    )  # Wait 25us for coil to ring down
    exp = PulseExperiment(tx_freq=25_090_230)
    data = exp.send_sequence(sequence=seq, rx_length_us=10e3)

    fid = FID1D(
        data=data,
        spectral_width=exp.sample_rate,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        observation_freq=exp.rx_freq,
        label="1H",
        sample="Water",
        pulse_file=f"single_90_degree_pulse,length={pulse_length_us}us,delay={delay_us}us",
        spectrometer="magnETHical v0.1",
    )
    timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
    fid.to_file(f"data/{timestr}-{fid.sample}-{fid.label}-{fid.pulse_file}.fid")

    # Since the amplitude of the signal is at 63.2% (1-1/e) at T2* one could try to estimate the decay here
    # A(t) = A0 * e^(-t/T2*) should be the decay of the sine wave
    # use the hilbert transform to get the envelope? see scipy.signals.hilbert

    # Plot raw data
    fig, axes = make_axes()
    axes.plot(fid.us_scale, fid.data, linestyle="", marker=".")
    axes.set_title(f"FID of {fid.label}")
    axes.set_ylabel("Amplitude")
    axes.set_xlabel("Time")
    style_axes(axes, nticks=4, xunit="μs", yunit="au")

    # Try to plot simple least squares fit
    try:
        # Try fitting the envelope
        envelope = np.abs(sps.hilbert(fid.data.real))
        fit_env = fit_decay(fid.us_scale, envelope)
        us_scale_fine = np.linspace(
            fid.us_scale[0], fid.us_scale[-1], len(fid.us_scale) * 10
        )
        axes.plot(us_scale_fine, fit_env["function"](us_scale_fine))

        # Try fitting the absolute directly
        fit_abs = fit_decay(fid.us_scale, np.abs(fid.data))
        axes.plot(us_scale_fine, fit_abs["function"](us_scale_fine))
    except (RuntimeError, ValueError, spo.OptimizeWarning) as err:
        logger.warning("Couldn't estimate curve fitting: %s", str(err))

    # Display plots
    fig.show()
    fid.show_plot()
    fid.show_simple_fft()
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
