import logging

import matplotlib.pyplot as plt
import numpy as np
import nmrglue as ng
from spectrometer.data import FID1D
from datetime import datetime, UTC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from marcos import Experiment


def send_simple_pulse(
    pulse_length_us=9,
    rx_length_us=10e3,
    label="Water 1H",
    tx0_freq=25e6,
    tx1_freq=None,
    rx_freq=None,
    sample_freq=320e3,
) -> None:
    # Setup marcos experiment
    tx1_freq = tx1_freq if tx1_freq else tx0_freq
    rx_freq = rx_freq if rx_freq else tx0_freq
    exp = Experiment(
        lo_freq=(tx0_freq / 1e6, tx1_freq / 1e6, rx_freq / 1e6),
        rx_lo=2,
        rx_t=1 / (sample_freq / 1e6),
    )
    sample_time_us_actual = exp.get_rx_ts()
    sample_freq_actual = (1 / sample_time_us_actual) * 1e6

    # Calculate TX/RX dictionary
    tx_start_us = 0
    tx_length_us = pulse_length_us
    tx_power = 1  # %

    tx_end_us = tx_start_us + tx_length_us

    # Make sure to not send a pulse while switching the gate
    tx_gate_pre_us = 1
    tx_gate_post_us = 1

    tx_rx_delay_us = 1  # must be >= tx_gate_post_us

    rx_start_us = tx_end_us + tx_rx_delay_us
    rx_end_us = rx_start_us + rx_length_us

    exp.add_flodict(
        {
            "tx0": (
                np.array([tx_start_us, tx_end_us]),
                np.array([tx_power, 0]),
            ),
            "tx_gate": (
                np.array([tx_start_us - tx_gate_pre_us, tx_end_us + tx_gate_post_us]),
                np.array([1, 0]),
            ),
            "rx0_en": (
                np.array([rx_start_us, rx_end_us]),
                np.array([1, 0]),
            ),
            "rx_gate": (
                np.array([rx_start_us, rx_end_us]),
                np.array([1, 0]),
            ),
        }
    )

    # Plot sequence (doesn´t show yet)
    sequence_fig, tx_axes = plt.subplots(
        4, 1, figsize=(12, 8), sharex="all", layout="constrained"
    )
    exp.plot_sequence(axes=tx_axes)

    # Execute the sequence
    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)

    # Log msgs
    logger.info(rxd)
    logger.info(msgs)

    # Create 1D FID object
    fid = FID1D(
        rxd["rx0"],
        spectral_width=sample_freq_actual,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        label=label,
        observation_freq=rx_freq,
    )
    timestr = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    labelstr = "".join([c for c in fid.label if c.isalnum() or c in "-_"])
    fid.to_file(f"{timestr}-{labelstr}.fid")

    # Display plots
    sequence_fig.show()
    fid.show_plot()
    fid.show_simple_fft()

    # freq_fft = np.fft.fftshift(np.fft.fftfreq(n=len(data), d=sample_time_us / 1e6))


if __name__ == "__main__":
    send_simple_pulse()
