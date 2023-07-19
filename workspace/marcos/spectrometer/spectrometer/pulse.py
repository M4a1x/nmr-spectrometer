import logging

import numpy as np
from marcos import Experiment
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from spectrometer.plot import make_axes, style_axes

logger = logging.getLogger(__name__)


def send_simple_pulse(
    pulse_length_us=9,
    rx_delay_us=35,
    rx_length_us=10e3,
    tx0_freq=25e6,
    tx1_freq=None,
    rx_freq=None,
    sample_freq=320e3,
) -> tuple[dict, float, Figure]:
    logger.info("Calculating pulse sequence and setting up experiment...")
    tx1_freq = tx1_freq if tx1_freq else tx0_freq
    rx_freq = rx_freq if rx_freq else tx0_freq
    exp = Experiment(
        lo_freq=(tx0_freq / 1e6, tx1_freq / 1e6, rx_freq / 1e6),
        rx_lo=2,
        rx_t=1 / (sample_freq / 1e6),
    )
    sample_time_us_actual = exp.get_rx_ts()[0]
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
                np.array([rx_start_us + rx_delay_us, rx_end_us + rx_delay_us]),
                np.array([1, 0]),
            ),
            "rx_gate": (
                np.array([rx_start_us, rx_end_us + rx_delay_us]),
                np.array([1, 0]),
            ),
        }
    )

    # Plot sequence (doesn`t show yet)
    sequence_fig, tx_axes = plt.subplots(
        4, 1, sharex="all", figsize=(12, 8), layout="constrained"
    )
    exp.plot_sequence(axes=tx_axes)

    # Execute the sequence
    logger.info("Executing experiment... Sending simple pulse sequence...")
    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)
    logger.info("Finished experiment run.")

    # Log results
    logger.info("Received experiment results: ")
    logger.info("Data:\n%s", rxd)
    logger.info("Messages:\n%s", msgs)

    return rxd["rx0"], sample_freq_actual, sequence_fig
