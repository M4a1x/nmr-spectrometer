import logging
import socket
import time
from typing import Iterable, Optional

import numpy as np
import numpy.typing as npt
from marcos import Experiment
from marcos.local_config import config

logger = logging.getLogger(__name__)


def send_sequence(
    tx0: tuple[npt.NDArray, npt.NDArray],
    rx_delay_us: float = 30,
    rx_length_us: float = 10e3,
    tx0_freq: float = 25e6,
    rx_freq: Optional[float] = None,
    sample_freq: float = 320e3,
    sock: Optional[socket.socket] = None,
) -> tuple[npt.NDArray, float]:
    """Send a sequence of pulses defined in the `tx0` tuple of arrays before switching to receive mode after
    a wait time of `rx_delay_us` after the last pulse ended.

    Args:
        tx0 (tuple[npt.NDArray, npt.NDArray]): contains two arrays with the first containing a list of
        event timestamps in us and the second a corresponding list of power levels. To send a simple pulse
        of 5us a tx0 of (np.array([0, 5], np.array([1, 0])) could be used. Which transmits full power
        directly at the beginning and then turns transmission off at 5us resulting in a single 5us pulse.
        rx_delay_us (int, optional): Wait time after the last event in the `tx0` array before the reception
        is turned on. Useful e.g. to wait for the coil ringing to end. Defaults to 30.
        rx_length_us (float, optional): . Defaults to 10e3.
        tx0_freq (float, optional): Frequency of the transmitted RF-Pulse. Should probably be equal to
        the expected resonant frequency of the Nuclei. Defaults to 25e6.
        rx_freq (float, optional): Frequency for the down-conversion. This will be the center of the
        resulting FT spectrum. If not provided will be the same as the `tx0_freq`.
        sample_freq (float, optional): Request sample frequency after downconversion. Inverse of the dwell time.
        Defaults to 320e3. Might be adjusted to the next closest frequency available. Check with the returned
        value.
        sock (socket.socket, optional): Socket that is connected to the pulse control server. If
        not provided will try to connect automatically. Required if this function is called more than once!

    Raises:
        ValueError: Function will do simple sanity checks and raise a ValueError if they fail

    Returns:
        tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
        QI-demodulation/downconversion, CIC-Filter and Sampling. The float contains the actual sampling
        rate used.
    """
    if np.any(tx0[0] < 0):
        msg = f"The time values of tx0 must be positive! Values are {tx0[0]}"
        raise ValueError(msg)
    if not np.all(np.diff(tx0[0]) > 0):
        msg = f"The time values of tx0 must be strictly monotonically increasing! Values are {tx0[0]}"
        raise ValueError(msg)

    logger.info("Calculating pulse sequence and setting up experiment...")
    tx1_freq = tx0_freq
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
    pulse_length_us: float = 9,
    rx_delay_us: float = 30,
    rx_length_us: float = 10e3,
    tx_freq: float = 25e6,
    rx_freq: Optional[float] = None,
    sample_freq: float = 320e3,
    sock: Optional[socket.socket] = None,
) -> tuple[npt.NDArray, float]:
    """Send a single simple pulse at frequency `tx_freq` with length `pulse_length_us`, wait for
    `rx_delay_us` and then receive for `rx_length_us`.

    The received signal will be a simple Free Induction Decay (FID) of the sample. It will decay with
    T2*.

    Args:
        pulse_length_us (int, optional): Length of the single pulse in us. Defaults to 9.
        rx_delay_us (int, optional): Time between end of the pulse and beginning of reception window.
        Defaults to 30.
        rx_length_us (float, optional): Length of the reception window. Defaults to 10e3.
        tx_freq (float, optional): Frequency of the pulse. Defaults to 25e6.
        rx_freq (float, optional): Frequency used for digital down conversion of the received signal.
        Will later be the center frequency of the FT spectrum. Will be equal to the transmission
        frequency if not provided. Defaults to None.
        sample_freq (float, optional): Request sample frequency after downconversion. Inverse of the dwell time.
        Defaults to 320e3. Might be adjusted to the next closest frequency available. Check with the returned
        value.
        sock (socket.socket, optional): Socket that is connected to the pulse control server. If
        not provided will try to connect automatically. Required if this function is called more than once!

    Returns:
        tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
        QI-demodulation/downconversion, CIC-Filter and Sampling. The float contains the actual sampling
        rate used.
    """
    # Wait for 10us before sending the pulse
    tx0 = (
        np.array([10, 10 + pulse_length_us]),
        np.array([1, 0]),
    )
    return send_sequence(
        tx0, rx_delay_us, rx_length_us, tx_freq, rx_freq, sample_freq, sock
    )


def send_simple_pulses(
    pulse_lengths_us: npt.NDArray | list[float],
    pulse_delay_s: float = 5,
    rx_delay_us: float = 30,
    rx_length_us: float = 10e3,
    tx_freq: float = 25e6,
    rx_freq: Optional[float] = None,
    sample_freq: float = 320e3,
) -> list[npt.NDArray]:
    """Send a `simple_pulse` multiple times with varying pulse lengths and wait in between for the
    system to return to rest.

    This is simply a convenience method for calling `send_simple_pulse` in a loop. The pulse length
    and rx time are accurate to the ns. The `pulse_delay_s` only to a couple of ms as it is dependent
    on the Linux host OS.

    Args:
        pulse_lengths_us (npt.NDArray | list[float]): Array containing a list of the pulses to be sent
        in sequential order in us, i.e. np.array([1,4, 7]) will send a 1us pulse, receive a signal after
        `rx_delay_us` then wait for `pulse_delay_s`, send a pulse of length 4us, wait for rx_delay_us, ...
        pulse_delay_s (float, optional): Time in seconds to wait between two
        experiments/`simple_pulses`. Defaults to 5.
        rx_delay_us (float, optional): Wait time between the end of the transmission pulse and starting
        to receive the signal, e.g. to wait for coil ringing to end. Defaults to 30.
        rx_length_us (float, optional): Length of the reception window. Defaults to 10e3.
        tx_freq (float, optional): Frequency of the transmitted pulse. Defaults to 25e6.
        rx_freq (float, optional): Frequency used for digital down conversion of the received signal.
        Will later be the center frequency of the FT spectrum. Will be equal to the transmission
        frequency if not provided. Defaults to None.
        sample_freq (float, optional): Request sample frequency after downconversion. Inverse of the dwell time.
        Defaults to 320e3. Might be adjusted to the next closest frequency available. Check with the returned
        value.

    Returns:
        tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
        QI-demodulation/downconversion, CIC-Filter and Sampling. The first dimension depends on
        the number of `simple_pulse`s/Experiments sent and the second dimension depends on the
        sampling frequency and length. The float contains the actual sampling rate used.
    """
    sock = _connect()
    fids = []
    for i, pulse_length_us in enumerate(pulse_lengths_us):
        logger.info(
            "Sending pulse %s/%s of length %sus...",
            i + 1,
            len(pulse_lengths_us),
            pulse_length_us,
        )
        data, sample_freq_actual = send_simple_pulse(
            pulse_length_us,
            rx_delay_us,
            rx_length_us,
            tx_freq=tx_freq,
            rx_freq=rx_freq,
            sample_freq=sample_freq,
            sock=sock,
        )
        fids.append(data)
        logger.info("Sleeping for %ss...", pulse_delay_s)
        time.sleep(pulse_delay_s)

    return fids, sample_freq_actual


def send_spin_echo(
    pulse_length_90_degree_us: float,
    delay_tau_us: float,
    rx_length_us: float = 10_000,
    tx_freq: float = 25e6,
    sample_freq: float = 320e3,
    sock: Optional[socket.socket] = None,
) -> tuple[npt.NDArray, float]:
    """Perform a simple conventional spin echo experiment. This function sends a 90 degree pulse
    as given, then waits for `delay_tau_us`, then sends a 180 degree pulse, waits `delay_tau_us` again
    and finally starts receiving the resulting spin echo.

    This experiment can be repeated several times with varying `delay_tau_us` to measure the T2 relaxation
    time of the sample, i.e. the change of the maximum amplitude of the echo with increasing delay.

    Args:
        pulse_length_90_degree_us (float): Length of a 90 degree pulse for the relevant Nuclei in us
        delay_tau_us (float): Time between the 90 degree and the 180 degree pulse, as well as the time
        between the 180 degree pulse and the start of the receiving window.
        rx_length_us (float, optional): Length of the reception window. Defaults to 10e3.
        tx_freq (float, optional): Frequency of the transmitted pulse. Defaults to 25e6.
        rx_freq (float, optional): Frequency used for digital down conversion of the received signal.
        Will later be the center frequency of the FT spectrum. Will be equal to the transmission
        frequency if not provided. Defaults to None.
        sample_freq (float, optional): Request sample frequency after downconversion. Inverse of the dwell time.
        Defaults to 320e3. Might be adjusted to the next closest frequency available. Check with the returned
        value.
        sock (socket.socket, optional): Socket that is connected to the pulse control server. If
        not provided will try to connect automatically. Required if this function is called more than once!

    Returns:
        tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
        QI-demodulation/downconversion, CIC-Filter and Sampling. The float contains the actual sampling
        rate used.
    """
    logger.info(
        "Creating Conventional Spin Echo Sequence: "
        "90 degree pulse of %sus, "
        "waiting tau=%sus, "
        "180 degree pulse of %sus.",
        pulse_length_90_degree_us,
        delay_tau_us,
        2 * pulse_length_90_degree_us,
    )
    pulse_90_start_us = 10
    pulse_90_end_us = pulse_90_start_us + pulse_length_90_degree_us
    pulse_180_start_us = pulse_90_end_us + delay_tau_us
    pulse_180_end_us = pulse_180_start_us + 2 * pulse_length_90_degree_us
    logger.info("Sending spin echo sequence...")
    return send_sequence(
        tx0=(
            np.array(
                [
                    pulse_90_start_us,
                    pulse_90_end_us,
                    pulse_180_start_us,
                    pulse_180_end_us,
                ]
            ),
            np.array([1, 0, 1, 0]),
        ),
        rx_delay_us=delay_tau_us,
        rx_length_us=rx_length_us,
        tx0_freq=tx_freq,
        sample_freq=sample_freq,
        sock=sock,
    )


def send_spin_echos(
    pulse_length_90_degree_us: float,
    delays_tau_us: npt.NDArray | Iterable[float],
    spin_echo_delay_s: float = 5,
    rx_length_us: float = 10_000,
    tx_freq: float = 25e6,
    sample_freq: float = 320e3,
) -> tuple[npt.NDArray, float]:
    """Send a `spin_echo` multiple times with varying delays tau between the 90 degree and 180 degree
    pulses and wait in between for the system to return to rest. Each spin echo consists of a 90
    degree pulse, a delay dau, a 180 degree pulse and again a delay of tau before measurement.
    For details see documentation for `send_spin_echo()`

    This is simply a convenience method for calling `send_spin_echo` in a loop. The pulse length,
    rx time and tau delay are accurate to the ns. The `spin_echo_delay_s` only to a couple of ms as
    it is dependent on the Linux host OS.

    Args:
        pulse_length_90_degree_us (float): Length of a 90 degree pulse for the relevant Nuclei in us
        delays_tau_us (npt.NDArray | list[float]): Time between the 90 degree and the 180 degree pulse,
        as well as the time between the 180 degree pulse and the start of the receiving window.
        rx_length_us (float, optional): Length of the reception window. Defaults to 10e3.
        tx_freq (float, optional): Frequency of the transmitted pulse. Defaults to 25e6.
        rx_freq (float, optional): Frequency used for digital down conversion of the received signal.
        Will later be the center frequency of the FT spectrum. Will be equal to the transmission
        frequency if not provided. Defaults to None.
        sample_freq (float, optional): Request sample frequency after downconversion. Inverse of the dwell time.
        Defaults to 320e3. Might be adjusted to the next closest frequency available. Check with the returned
        value.

    Returns:
        tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
        QI-demodulation/downconversion, CIC-Filter and Sampling. The first dimension depends on
        the number of `pulse_echo`s/Experiments sent and the second dimension depends on the
        sampling frequency and length. The float contains the actual sampling rate used.
    """
    sock = _connect()
    fids = []
    for i, delay_tau_us in enumerate(delays_tau_us):
        logger.info("Spin Echo %s/%s...", i + 1, len(delays_tau_us))
        data, sample_freq_actual = send_spin_echo(
            pulse_length_90_degree_us,
            delay_tau_us,
            rx_length_us,
            tx_freq=tx_freq,
            sample_freq=sample_freq,
            sock=sock,
        )
        fids.append(data)
        logger.info("Sleeping for %ss...", spin_echo_delay_s)
        time.sleep(spin_echo_delay_s)

    return fids, sample_freq_actual


def _connect() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # 5s timeout
    sock.connect((config["ip_address"], config["port"]))
    return sock
