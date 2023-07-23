import logging
import socket
import time

import numpy as np
import numpy.typing as npt
from marcos import Experiment
from marcos.local_config import config

logger = logging.getLogger(__name__)


def send_sequence(
    tx0: tuple[npt.NDArray, npt.NDArray],
    rx_delay_us=30,
    rx_length_us=10e3,
    tx0_freq=25e6,
    tx1_freq=None,
    rx_freq=None,
    sample_freq=320e3,
    sock=None,
) -> tuple[npt.NDArray, float]:
    if np.any(tx0[0] < 0):
        msg = f"The time values of tx0 must be positive! Values are {tx0[0]}"
        raise ValueError(msg)
    if not np.all(np.diff(tx0[0]) > 0):
        msg = f"The time values of tx0 must be strictly monotonically increasing! Values are {tx0[0]}"
        raise ValueError(msg)

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
    if not np.allclose(sample_freq, sample_freq_actual):
        msg = f"Invalid sampling frequency of {sample_freq}. Next closest sampling frequency is {sample_freq_actual}"
        raise ValueError(msg)

    # Get TX envelope times
    tx_start_us = tx0[0][0]
    tx_end_us = tx0[0][-1]

    # Make sure to not send a pulse while switching the gate
    tx_gate_pre_us = 1
    tx_gate_post_us = 1

    tx_rx_gate_delay_us = 1  # must be >= tx_gate_post_us
    if rx_delay_us <= tx_rx_gate_delay_us:
        msg = f"Delay between TX and RX must be greater than {tx_rx_gate_delay_us}us. Current delay: {rx_delay_us}us."
        raise ValueError(msg)

    rx_gate_start_us = tx_end_us + tx_rx_gate_delay_us
    rx_start_us = tx_end_us + rx_delay_us
    rx_end_us = rx_start_us + rx_length_us
    rx_gate_end_us = rx_end_us + 1

    exp.add_flodict(
        {
            "tx0": tx0,
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

    # Execute the sequence
    logger.info("Executing experiment: Sending simple pulse sequence...")
    rxd, msgs = exp.run()
    logger.info("Finished experiment run.")

    # Log results
    logger.info("Received experiment results: ")
    logger.info("Data:\n%s", rxd)
    logger.info("Messages:\n%s", msgs)

    return rxd["rx0"], sample_freq_actual


def send_simple_pulse(
    pulse_length_us=9,
    rx_delay_us=30,
    rx_length_us=10e3,
    tx0_freq=25e6,
    tx1_freq=None,
    rx_freq=None,
    sample_freq=320e3,
    sock=None,
) -> tuple[npt.NDArray, float]:
    # Wait for 10us before sending the pulse
    tx0 = (
        np.array([10, 10 + pulse_length_us]),
        np.array([1, 0]),
    )
    return send_sequence(
        tx0, rx_delay_us, rx_length_us, tx0_freq, tx1_freq, rx_freq, sample_freq, sock
    )


def send_varying_pulses(
    pulse_lengths_us: npt.NDArray,
    pulse_delay_s=5,
    rx_delay_us=30,
    rx_length_us=10e3,
    tx_freq=25e6,
    sample_freq=320e3,
) -> list[npt.NDArray]:
    sock = _connect()
    fids = []
    for i, pulse_length_us in enumerate(pulse_lengths_us):
        logger.info(
            "Sending pulse %s/%s of length %sus...",
            i + 1,
            len(pulse_lengths_us),
            pulse_length_us,
        )
        data, _sample_freq_actual = send_simple_pulse(
            pulse_length_us,
            rx_delay_us,
            rx_length_us,
            tx0_freq=tx_freq,
            tx1_freq=None,
            rx_freq=None,
            sample_freq=sample_freq,
            sock=sock,
        )
        fids.append(data)
        logger.info("Sleeping for %ss...", pulse_delay_s)
        time.sleep(pulse_delay_s)

    return fids


def send_spin_echo() -> None:
    raise NotImplementedError()


def _connect() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # 5s timeout
    sock.connect((config["ip_address"], config["port"]))
    return sock
