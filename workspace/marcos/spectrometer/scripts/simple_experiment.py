#!/usr/bin/env python3

import logging
from datetime import UTC, datetime

import matplotlib.pyplot as plt

from spectrometer.data import FID1D
from spectrometer.pulse import send_simple_pulse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    freq = 25_090_230
    label = "Water 1H"
    data, sample_freq, sequence_fig = send_simple_pulse(
        pulse_length_us=1,
        rx_delay_us=25,  # wait between pulse and acquisition for coil to ring down
        rx_length_us=10e3,
        tx0_freq=freq,
    )

    # Create 1D FID object
    fid = FID1D(
        data,
        spectral_width=sample_freq,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        label=label,
        observation_freq=freq,
    )
    timestr = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    labelstr = "".join([c if (c.isalnum() or c in "-_") else "_" for c in fid.label])
    fid.to_file(f"{timestr}-{labelstr}.fid")

    # Display plots
    sequence_fig.show()
    fid.show_plot()
    fid.show_simple_fft()
    plt.show(block=True)


if __name__ == "__main__":
    main()
