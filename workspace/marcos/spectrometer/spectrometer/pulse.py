import logging
import socket
import time

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from marcos import Experiment
from matplotlib.figure import Figure

from spectrometer.plot import make_axes, style_axes

logger = logging.getLogger(__name__)

ip_address = "192.168.1.100"
port = 11111
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((ip_address, port))


def send_simple_pulse(
    pulse_length_us=9,
    rx_delay_us=30,
    rx_length_us=10e3,
    tx0_freq=25e6,
    tx1_freq=None,
    rx_freq=None,
    sample_freq=320e3,
) -> tuple[npt.NDArray, float, Figure]:
    logger.info("Calculating pulse sequence and setting up experiment...")
    tx1_freq = tx1_freq if tx1_freq else tx0_freq
    rx_freq = rx_freq if rx_freq else tx0_freq
    exp = Experiment(
        lo_freq=(tx0_freq / 1e6, tx1_freq / 1e6, rx_freq / 1e6),
        rx_lo=2,
        rx_t=1 / (sample_freq / 1e6),
        prev_socket=sock,
        halt_and_reset=True,
        flush_old_rx=True,
        assert_errors=False,
    )
    sample_time_us_actual = exp.get_rx_ts()[0]
    sample_freq_actual = (1 / sample_time_us_actual) * 1e6

    # Calculate TX/RX dictionary
    tx_start_us = 10
    tx_length_us = pulse_length_us
    tx_power = 1  # %

    tx_end_us = tx_start_us + tx_length_us

    # Make sure to not send a pulse while switching the gate
    tx_gate_pre_us = 1
    tx_gate_post_us = 1

    tx_rx_gate_delay_us = 1  # must be >= tx_gate_post_us

    rx_gate_start_us = tx_end_us + tx_rx_gate_delay_us
    rx_start_us = tx_end_us + rx_delay_us
    rx_end_us = rx_start_us + rx_length_us
    rx_gate_end_us = rx_end_us + 1

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
                np.array([rx_gate_start_us, rx_gate_end_us]),
                np.array([1, 0]),
            ),
        }
    )

    # Plot sequence (doesn`t show yet)
    # sequence_fig, tx_axes = plt.subplots(
    #     4, 1, sharex="all", figsize=(12, 8), layout="constrained"
    # )
    # exp.plot_sequence(axes=tx_axes)

    # Execute the sequence
    logger.info("Executing experiment: Sending simple pulse sequence...")
    rxd, msgs = exp.run()
    logger.info("Finished experiment run.")

    # Log results
    logger.info("Received experiment results: ")
    logger.info("Data:\n%s", rxd)
    logger.info("Messages:\n%s", msgs)

    return rxd["rx0"], sample_freq_actual, None  # sequence_fig


def send_varying_pulses(
    pulse_lengths_us,
    pulse_delay_s=10,
    rx_delay_us=30,
    rx_length_us=10e3,
    freq=25e6,
    sample_freq=320e3,
) -> npt.NDArray:
    peaks = np.empty_like(pulse_lengths_us, dtype=np.float64)
    for i, pulse_length_us in enumerate(pulse_lengths_us):
        logger.info(
            "Sending pulse %s/%s of length %sus...", i + 1, len(peaks), pulse_length_us
        )
        data, _, _ = send_simple_pulse(
            pulse_length_us,
            rx_delay_us,
            rx_length_us,
            tx0_freq=freq,
            tx1_freq=None,
            rx_freq=None,
            sample_freq=sample_freq,
        )
        peaks[i] = np.max(np.abs(data))
        logger.info("Sleeping for %ss...", pulse_delay_s)
        time.sleep(pulse_delay_s)

    return peaks
