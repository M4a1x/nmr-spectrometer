import ipaddress
import logging
import socket
import time
from collections.abc import Iterable
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Self

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from marcos import Experiment
from marcos.local_config import config

logger = logging.getLogger(__name__)

# TODO: Probably better to move RX "calculation" into the PulseSequence class, especially if the
# user wants to receive multiple times within a sequence/between pulses (currently in
# PulseExperiment)


class SpectrometerConfig:
    """Simple container containing the necessary information to connect to the spectrometer and
    verify the viability of the requested excitation pulses"""

    def __init__(
        self,
        ip_address: Optional[IPv4Address | IPv6Address] = None,
        port: Optional[int] = None,
        fpga_clock_freq: Optional[float] = None,
    ) -> None:
        """Create new Sepctrometer config

        Args:
            ip_address (IPv4Address | IPv6Address, optional): IP address of the spectrometer. If
            None, tries to load address from config. Defaults to None.
            port (int, optional): Network Port of the spectrometer. If None, tries to load the port
            from config. Defaults to None.
            fpga_clock_freq (float, optional): Frequency of the FPGA clock. If None, tries to load
            the frequency from config. Defaults to None.
        """
        self.ip_address = (
            ip_address if ip_address else ipaddress.ip_address(config["ip_address"])
        )
        self.port = port if port else int(config["port"])
        self.fpga_clock_freq = (
            fpga_clock_freq
            if fpga_clock_freq
            else float(config["fpga_clock_freq_MHz"]) * 1e6
        )

    @property
    def socket_config(self) -> tuple[str, str]:
        """Returns a tuple to pass to socket.socket for connecting to the spectrometer"""
        return str(self.ip_address), str(self.port)


class PulseSequence:
    """Class representing a TX Pulse sequence that can be sent by a `PulseExperiment`"""

    def __init__(self, sequence: tuple[npt.NDArray, npt.NDArray]) -> None:
        """Takes a tuple of two numpy arrays to create a pulse sequence.

        The first array contains the timestamps at which the transmission changes. The second array
        contains the corresponding power level the transmission should be changed to.
        To send a simple pulse of 5us a sequence of (np.array([0, 5], np.array([1, 0])) could be
        used. Which transmits full power directly at the beginning and then turns transmission off
        at 5us resulting in a single 5us pulse.

        The power level array can contain complex numbers, which then indicate the phase of
        the pulse.

        The value of the power level can be repeated. This can be useful e.g. to include a defined
        wait period (by resending a power level of 0) after a sequence before receiving
        should start (e.g. for pulse echo experiments)

        Args:
            sequence (tuple[npt.NDArray, npt.NDArray]): Tuple containing event timestamps and
            corresponding power level (incl. phase)

        Raises:
            ValueError: Sanity checks are performed. Raises if sequence is impossible or
            contains errors
        """
        if len(sequence[0]) != len(sequence[1]):
            msg = (
                "Event Timestamps and Power Levels must match in length. Every timestamp needs a "
                "corresponding power level to set the output to"
            )
            raise ValueError(msg)
        if np.iscomplex(sequence[0]):
            msg = (
                "Complex time (unfortunately) isn't a thing here! Make sure the first array "
                "contains only real valued timestamps in us"
            )
            raise ValueError(msg)
        if np.any(sequence[0] < 0):
            msg = f"The time values of sequence must be positive! Values are {sequence[0]}"
            raise ValueError(msg)
        if not np.all(np.diff(sequence[0]) > 0):
            msg = f"The time values of sequence must be strictly monotonically increasing! Values are {sequence[0]}"
            raise ValueError(msg)
        if sequence[1][-1] != 0:
            msg = (
                "The last pulse needs to end! The power of the transmission signal needs to "
                f"return to zero in the pulse sequence. Values are {sequence[1]}"
            )
            raise ValueError(msg)
        self.sequence = sequence

    @classmethod
    def simple(cls, pulse_length_us: float, delay_us: float) -> Self:
        """Generate a single simple pulse (p1) with length `pulse_length_us` and a wait time of
        `delay_us` after that.

        The received signal will be a simple Free Induction Decay (FID) of the sample,
        It will decay with T2* if executed as independent experiment.

                <  p1  >
                ┌──────┐
                │      │
                │      │<     delay     >
        ────────┘      └─────────────────

        Args:
            pulse_length_us (float): Length of the single pulse in us (p1)
            delay_us (float): Length of the wait time in us (d1)

        Returns:
            Self: Sequence of a single pulse with given length
        """
        sequence = (
            np.array([0, pulse_length_us, pulse_length_us + delay_us]),
            np.array([1, 0, 0]),
        )
        return cls(sequence)

    @classmethod
    def spin_echo(cls, pulse_length_us: float, delay_us: float) -> Self:
        """Generate a spin echo sequence with the given 90 degree pulse length (p1) and the given
        delay between the 90 degree pulse (p1) and the 180 degree pulse (p2) as well as the
        180 degree pulse (p2) and acquisition.

        If multiple spin echos are recorded with increasing `delay_us` the T2 relaxation time can
        be estimated through the maxima of the spin echo signals.

                <  p1  >                 <     p2     >
                ┌──────┐                 ┌────────────┐
                │      │                 │            │
                │      │<     delay     >│            │<     delay     >
        ────────┘      └─────────────────┘            └─────────────────
                   90°                        180°

        Args:
            pulse_length_us (float): Length of a 90 degree pulse for the relevant Nuclei in us (p1)
            delay_us (float):  Time between the 90 degree and the 180 degree pulse, as well as
            the time (d12) between the 180 degree pulse and the start of the receiving window.

        Returns:
            Self: Pulse sequence describing a conventional pulse echo experiment
        """
        pulse_90_start_us = 0
        pulse_90_end_us = pulse_90_start_us + pulse_length_us
        pulse_180_start_us = pulse_90_end_us + delay_us
        pulse_180_end_us = pulse_180_start_us + 2 * pulse_length_us
        sequence_end_us = pulse_180_end_us + delay_us
        sequence = (
            np.array(
                [
                    pulse_90_start_us,
                    pulse_90_end_us,
                    pulse_180_start_us,
                    pulse_180_end_us,
                    sequence_end_us,
                ]
            ),
            np.array([1, 0, 1, 0, 0]),
        )
        return cls(sequence)


class PulseExperiment:
    """Class containing the basic information on an experiment (mixing frequencies,
    sampling rate, server information, ...) as well as managing the connection state of
    the spectrometer.

    Instantiate this class with the required parameters and then use the `send_sequence()` or
    `send_sequences()` functions to perform experiments (i.e. send pulses and acquire a signal).
    """

    def __init__(
        self,
        tx_freq: float,
        rx_freq: Optional[float] = None,
        sample_rate: float = 320e3,
        server_config: Optional[SpectrometerConfig] = None,
    ) -> None:
        """Create new basic experiment configuration and connect to the spectrometer.

        After instantiation pulse sequence(s) can be send with the respective `send_...()`
        functions.

        Args:
            rx_delay_us (float): Wait time after the end of a pulse sequence (i.e. the last event in
            the sequence) before the reception is turned on. Useful e.g. for waiting for the coil
            ringing to end.
            tx_freq (float): Frequency of the transmitted RF-Pulse. Should probably be equal to
            the expected resonant frequency of the Nuclei.
            rx_freq (float | None, optional): Frequency for the down-conversion during reception.
            This will be the center of the resulting FT spectrum. If None the same frequency as
            `tx_freq` will be used. Defaults to None.
            sample_rate (float, optional): Request sample frequency after downconversion.
            Inverse of the dwell time. Defaults to 320kSPS.
            server_config (ServerConfig | None, optional): Configuration of the spectrometer. If
            None tries to load it from configuration file. If no config file is found a default
            one will be used. Defaults to None.

        Raises:
            ValueError: Function will do simple sanity checks and raise a ValueError if they fail
            socket.error: If there's an error with the network connection to the spectrometer server
        """
        rx_freq = rx_freq if rx_freq else tx_freq
        server_cfg = server_config if server_config else SpectrometerConfig()
        if sample_rate <= 0:
            msg = f"The the sample_rate must be positive and not zero! {sample_rate}Hz is invalid."
            raise ValueError(msg)
        if tx_freq < 0 or rx_freq < 0:
            msg = (
                f"The TX and RX frequencies can't be negative! "
                f"They were {tx_freq} and {rx_freq} respectively"
            )
            raise ValueError(msg)
        if not (server_cfg.fpga_clock_freq / sample_rate).is_integer():
            msg = (
                f"Sample time must be an integer multiple of the time between two clock "
                f"cycles of the FPGA! The chosen RX frequency of {rx_freq}Hz results in "
                f"a sample time of {1/rx_freq}s. The FPGA frequency of "
                f"{server_cfg.fpga_clock_freq}Hz results in a FPGA cycle time of "
                f"{1/server_cfg.fpga_clock_freq}s. Thus the next closest multiple would be"
                f"{server_cfg.fpga_clock_freq/np.round(server_cfg.fpga_clock_freq/sample_rate)}Hz."
            )
            raise ValueError(msg)

        self.tx_freq = tx_freq
        self.rx_freq = rx_freq
        self.sample_rate = sample_rate
        self.socket = self._connect(*server_cfg.socket_config)

    def send_sequence(
        self, sequence: PulseSequence, rx_length_us: float, *, debug: bool = False
    ) -> npt.NDArray:
        """Send the given excitation pulse sequence to the probe and receive a signal for
        `rx_length_us` after the end of the pulse

        Args:
            sequence (PulseSequence): Event sequence describing a pulse experiment. For details see
            `PulseSequence` documentation
            rx_length_us (float): Length in us to receive data for

        Returns:
            tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
            QI-demodulation/downconversion, CIC-filter and sampling.
        """
        logger.info("Setting up experiment...")
        exp = Experiment(
            lo_freq=(
                self.tx_freq / 1e6,  # tx0 channel
                self.tx_freq / 1e6,  # tx1 channel
                self.rx_freq / 1e6,  # rx  channels (rx0 and rx1)
            ),  # tx0, tx1, rx
            rx_lo=2,
            rx_t=(1 / self.sample_rate) * 1e6,
            prev_socket=self.socket,
            halt_and_reset=True,
            flush_old_rx=True,
            assert_errors=False,
        )

        # Move all timestamps 10us to the future to make room for RX switching as timestamps need
        # to be positive
        sequence[0] += 10

        # Get TX gate envelope times.
        # Don't transmit while switching or transmit gate is off!
        tx_gate_pre_us = 1
        tx_gate_post_us = 1
        start_first_pulse_us = sequence[0][np.nonzero(sequence[1])[0][0]]
        end_last_pulse_us = sequence[0][np.nonzero(sequence[1])[0][-1] + 1]
        tx_gate_on_us = start_first_pulse_us - tx_gate_pre_us
        tx_gate_off_us = end_last_pulse_us + tx_gate_post_us

        # Receive after the whole tx sequence is over
        tx_end_us = sequence[0][-1]
        rx_start_us = tx_end_us
        rx_end_us = rx_start_us + rx_length_us

        # Switch RX gate right after the TX gate (can't switch gates simultaneously)
        rx_gate_on_us = tx_gate_off_us
        rx_gate_off_us = rx_end_us + 1

        exp.add_flodict(
            {
                "tx0": sequence,
                "tx_gate": (
                    np.array([tx_gate_on_us, tx_gate_off_us]),
                    np.array([1, 0]),
                ),
                "rx0_en": (
                    np.array([rx_start_us, rx_end_us]),
                    np.array([1, 0]),
                ),
                "rx_gate": (
                    np.array([rx_gate_on_us, rx_gate_off_us]),
                    np.array([1, 0]),
                ),
            }
        )

        logger.info("Executing experiment: Sending simple pulse sequence...")
        rxd, msgs = exp.run()
        logger.info("Finished experiment run.")

        logger.info("Received experiment results: ")
        logger.info("Data:\n%s", rxd)
        logger.info("Messages:\n%s", msgs)

        if debug:
            exp.plot_sequence()
            plt.show()

        return rxd["rx0"]

    def send_sequences(
        self,
        sequences: Iterable[tuple[npt.NDArray, npt.NDArray]],
        rx_length_us: float,
        repetition_time_s: float,
    ) -> list[npt.NDArray]:
        """Send a list of sequences while waiting `repetition_time_s` seconds in between each
        sequence to wait for the system to return to rest.

        This is simply a convenience method for calling `send_sequence()` in a loop. The pulse
        sequence timings are accurate to the ns. The `pulse_delay_s` is only accurate to a couple
        of ms as it is dependent on the Linux host OS timers and scheduler, so don't rely on its
        accuracy.

        Args:
            sequences (Iterable[tuple[npt.NDArray, npt.NDArray]]): List of multiple sequences to be
            sent
            rx_length_us (float): Length of the receiving window after every pulse sequence,
            accurate to the ns.
            repetition_time_s (float): Time to wait between executing the sequences. Done via
            a simple python time.sleep(repetition_time_s)

        Returns:
            npt.NDArray: List of flat arrays with the received (complex) data in time domain after
            QI-demodulation/downconversion, CIC-filter and sampling ordered according to the input.
        """
        fids = []
        for i, sequence in enumerate(sequences):
            logger.info("Sending sequence %s/%s...", i + 1, len(sequences))
            data = self.send_sequence(sequence, rx_length_us)
            fids.append(data)
            logger.info("Sleeping for %ss...", repetition_time_s)
            time.sleep(repetition_time_s)

        return fids

    @staticmethod
    def _connect(ip_address, port) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5s timeout for all commands
        sock.connect((ip_address, port))
        return sock
