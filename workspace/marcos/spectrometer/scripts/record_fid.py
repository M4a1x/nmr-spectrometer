#!/usr/bin/env python3

import logging

import matplotlib.pyplot as plt

from spectrometer import FID1D, PulseExperiment, PulseSequence

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

    # Display plots
    fid.show_plot()
    fid.show_simple_fft()
    plt.show(block=True)


if __name__ == "__main__":
    main()
