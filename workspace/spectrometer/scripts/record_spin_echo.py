#!/usr/bin/env python3
import logging

import matplotlib.pyplot as plt

from spectrometer import FID1D, NMRSequence, PulseExperiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    # Send Spin Echo
    pulse_length_us = 9
    delay_us = 4e3
    exp = PulseExperiment(tx_freq=25_090_230)
    sequence = NMRSequence.spin_echo(pulse_length_us, delay_us)
    data = exp.send_sequence(sequence=sequence, rx_length_us=10e3)

    # Save FID
    fid = FID1D(
        data=data,
        spectral_width=exp.sample_rate,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        observation_freq=exp.rx_freq,
        label="1H",
        sample="Water",
        pulse_file=f"spin_echo,length={pulse_length_us}us,delay={delay_us}us",
        spectrometer="magnETHical v0.1",
    )
    timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
    fid.to_file(f"data/{timestr}-{fid.sample}-{fid.label}-{fid.pulse_file}.fid")

    # Plot
    fid.show_plot()
    plt.show(block=True)


if __name__ == "__main__":
    main()
