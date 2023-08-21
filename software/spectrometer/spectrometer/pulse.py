"""Module for creating, sending and receiving NMR pulse sequences

The `SpectrometerConfig` contains the relevant configuration for the spectrometer. This includes
where to find it (IP address and network port) and the internal clock frequency (depends on the
hardware used). If no values are supplied the __init__ will try to load them from a
`local_config.toml` from the current directory or use default values if no config is found.

A `PulseSequence` object contains all information describing an NMR pulse sequence. Convenience
classmethods exist for creating simple pulses like a single pulse or a standard pulse echo sequence.
Custom sequences can be created by directly supplying the two arrays with the timestamps and
corresponding power levels (see `PulseSequence` docs) or through the object oriented programming
interface by creating a list of `Pulse`s, `Delay`s and and `Record`s and passing that to the
`PulseSequence.build()` classmethod.

A `PulseExperiment` can be created by supplying a `SpectrometerConfig` to it. Then sequences can
be sent through the `send_sequence` and `send_sequences` methods, called on a `PulseExperiment`.
"""
import ipaddress
import logging
import shutil
import socket
import tempfile
import time
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Self
from urllib import request

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from fabric import Connection
from marcos import Experiment
from marcos.local_config import config

logger = logging.getLogger(__name__)
MARCOS_EXTRAS_URL = "https://github.com/vnegnev/marcos_extras/raw/77df0e4a33cec07eb751f0b1947a6aead99e8478"
MARCOS_SERVER_URL = (
    "https://github.com/vnegnev/marcos_server/archive/refs/heads/master.zip"
)

# TODO: Probably better to move RX "calculation" into the PulseSequence class, especially if the
# user wants to receive multiple times within a sequence/between pulses (currently in
# PulseExperiment)


class ConnectionSettings:
    """Simple container containing the necessary information to connect to the spectrometer and
    verify the viability of the requested excitation pulses"""

    def __init__(
        self,
        ip_address: IPv4Address | IPv6Address | None = None,
        port: int | None = None,
        fpga_clock_freq: float | None = None,
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
            ip_address
            if ip_address
            else ipaddress.ip_address(config["server"]["ip_address"])
        )
        self.port = port if port else int(config["server"]["port"])
        self.fpga_clock_freq = (
            fpga_clock_freq
            if fpga_clock_freq
            else float(config["server"]["fpga_clk_freq_MHz"]) * 1e6
        )

    @property
    def socket_config(self) -> tuple[str, str]:
        """Returns a tuple to pass to socket.socket for connecting to the spectrometer"""
        return str(self.ip_address), self.port


class Pulse:
    """Represents a single NMR pulse with power, duration and phase"""

    def __init__(
        self, duration_us: float, power: float = 1, phase_rad: float = 0
    ) -> None:
        if power < 0 or power > 1:
            msg = "Power must be from 0 to 1"
            raise ValueError(msg)
        if duration_us < 0:
            msg = "Pulse durations can only be positive"
            raise ValueError(msg)

        self.power = power
        self.duration_us = duration_us
        self.phase_rad = phase_rad % (2 * np.pi)

    @property
    def pulse_complex(self) -> complex:
        """Returns the power and phase as complex number with the magnitude (between 0 and 1)
        representing the power and the phase represented by the complex phase.

        >>> c = self.power * np.exp(1j * self.phase_rad)
        """

        return self.power * np.exp(1j * self.phase_rad)


class Delay:
    """Represents a delay in us within an NMR pulse sequence"""

    def __init__(self, duration_us: float) -> None:
        if duration_us < 0:
            msg = "Delay durations can only be positive"
            raise ValueError(msg)
        self.duration_us = duration_us


class Record:
    """Represents an NMR record command within an NMR pulse sequence.

    Note: This does not store the recorded data! This is only for defining
    an NNR sequence
    """

    def __init__(self, duration_us: float) -> None:
        if duration_us < 0:
            msg = "Delay durations can only be positive"
            raise ValueError(msg)
        self.duration_us = duration_us


# TODO: Implement Pulseq support
class NMRSequence:
    """Class representing an NMR Pulse sequence that can be sent by a `PulseExperiment`
    consisting of a transmit sequence of pulses and a receive sequence describing when to record
    data."""

    def __init__(
        self, tx_sequence: tuple[npt.NDArray, npt.NDArray], rx_sequence: npt.NDArray
    ) -> None:
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
        if len(tx_sequence[0]) != len(tx_sequence[1]):
            msg = (
                "Event timestamps and power levels must match in length. Every timestamp needs a "
                "corresponding power level to set the output to"
            )
            raise ValueError(msg)
        if np.any(np.iscomplex(tx_sequence[0])):
            msg = (
                "Complex time (unfortunately) isn't a thing here! Make sure the first array "
                "contains only real valued timestamps in us"
            )
            raise ValueError(msg)
        if np.any(tx_sequence[0] < 0):
            msg = f"The time values of sequence must be positive! Values are {tx_sequence[0]}"
            raise ValueError(msg)
        if not np.all(np.diff(tx_sequence[0]) > 0):
            msg = (
                "The time values of sequence must be strictly monotonically increasing! "
                f"Values are {tx_sequence[0]}"
            )
            raise ValueError(msg)
        if len(tx_sequence[1]) > 0 and tx_sequence[1][-1] != 0:
            msg = (
                "The last pulse needs to end! The power of the transmission signal needs to "
                f"return to zero in the pulse sequence. Values are {tx_sequence[1]}"
            )
            raise ValueError(msg)
        if np.any(rx_sequence < 0):
            msg = (
                "The time values of the record sequence must be positive!"
                f"Values are {rx_sequence}"
            )
            raise ValueError(msg)
        if not np.all(np.diff(rx_sequence) > 0):
            msg = (
                "The time values of the record sequence must be "
                f"strictly monotonically increasing! Values are {rx_sequence}"
            )
            raise ValueError(msg)
        if len(rx_sequence) % 2 != 0:
            msg = (
                "The recording needs to end, "
                "thus the recording sequence needs to have an even number of elements!"
                f"Values are: {rx_sequence}"
            )
            raise ValueError(msg)

        # Find pulse edge indexes
        tx_p = np.concatenate(([0], tx_sequence[1]))
        pulse_start_idx = np.nonzero((tx_p[:-1] == 0) & (tx_p[1:] != 0))[0]
        pulse_end_idx = np.nonzero((tx_p[:-1] != 0) & (tx_p[1:] == 0))[0]

        # Find pulse and recording start and end times
        pulse_starts = tx_sequence[0][pulse_start_idx]
        pulse_ends = tx_sequence[0][pulse_end_idx]
        record_starts = rx_sequence[::2]
        record_ends = rx_sequence[1::2]

        # Use numpy broadcasting for overlap check
        # Make sure that there is at least a 1us buffer between
        # transmit and receive and receive and transmit
        overlap = np.any(
            (pulse_starts < (record_ends[:, np.newaxis] + 1))
            & ((pulse_ends + 1) > record_starts[:, np.newaxis])
        )
        if overlap:
            msg = (
                "Can't receive and transmit simultaneously! There needs to be a delay of at least "
                "1us between transmit and receive and 1us between receive and transmit"
            )
            raise ValueError(msg)

        self.tx_sequence = tx_sequence
        self.rx_sequence = rx_sequence

    @classmethod
    def empty(cls) -> Self:
        return cls((np.empty(0), np.empty(0)), np.empty(0))

    @classmethod
    def build(cls, sequence: Sequence[Pulse | Delay | Record]) -> Self:
        tx_powers = []
        tx_times_us = []
        rx_times_us = []

        current_time_us = 0
        for event in sequence:
            match event:
                case Pulse(duration_us=duration_us, pulse_complex=tx_power):
                    # Pulse start
                    tx_powers.append(tx_power)
                    tx_times_us.append(current_time_us)
                    current_time_us += duration_us

                    # Pulse end
                    tx_powers.append(0)
                    tx_times_us.append(current_time_us)
                case Delay(duration_us=duration_us):
                    # Increase time
                    current_time_us += duration_us
                case Record(duration_us=duration_us):
                    # Start recording
                    rx_times_us.append(current_time_us)
                    current_time_us += duration_us

                    # End recording
                    rx_times_us.append(current_time_us)
                case default:
                    msg = f"Unknown object found in pulse sequence: {default}"
                    raise ValueError(msg)

        return cls((np.array(tx_times_us), np.array(tx_powers)), np.array(rx_times_us))

    @classmethod
    def simple(
        cls, pulse_length_us: float, delay_us: float, record_length_us: float
    ) -> Self:
        """Generate a single simple pulse (p1) with length `pulse_length_us` and a wait time of
        `delay_us` after that, then record the signal for `record_length_us`.

        The received signal will be a simple Free Induction Decay (FID) of the sample,
        It will decay with T2* if executed as independent experiment.

                < pulse >
                ┌───────┐
                │       │
                │       │<     delay     ><   record   >
        ────────┘       └───────────────────────────────

        Args:
            pulse_length_us (float): Length of the single pulse in us (p1)
            delay_us (float): Length of the wait time in us (d1)
            record_length_us (float): Length of the recording of the received signal in us

        Returns:
            Self: Sequence of a single pulse with given length
        """
        tx_sequence = (
            np.array([0, pulse_length_us]),
            np.array([1, 0]),
        )
        rx_sequence = np.array(
            [pulse_length_us + delay_us, pulse_length_us + delay_us + record_length_us]
        )
        return cls(tx_sequence, rx_sequence)

    @classmethod
    def spin_echo(
        cls,
        pulse_length_us: float,
        delay_tau_us: float,
        delay_after_p2_us: float,
        record_length_us: float,
    ) -> Self:
        """Generate a spin echo sequence with the given 90 degree pulse length (p1) and the given
        delay between the 90 degree pulse (p1) and the 180 degree pulse (p2) as well as the
        180 degree pulse (p2) and acquisition.

        If multiple spin echoes are recorded with increasing `delay_tau_us` the T2 relaxation time can
        be estimated through the maxima of the spin echo signals.

                <  p1  >                 <     p2     >
                ┌──────┐                 ┌────────────┐
                │      │                 │            │
                │      │<   delay_tau   >│            │< delay_after_p2 >
        ────────┘      └─────────────────┘            └──────────────────
                   90°                        180°

        Args:
            pulse_length_us (float): Length of a 90 degree pulse for the relevant Nuclei in us (p1)
            delay_tau_us (float):  Time between the 90 degree and the 180 degree pulse, as well as
            the time (d12) between the 180 degree pulse and the start of the receiving window.
            delay_after_p2_us (float): Time to wait after the second pulse before starting a recording
            record_length_us (float): Time to record the FID

        Returns:
            Self: Pulse sequence describing a conventional pulse echo experiment
        """
        pulse_90_start_us = 0
        pulse_90_end_us = pulse_90_start_us + pulse_length_us
        pulse_180_start_us = pulse_90_end_us + delay_tau_us
        pulse_180_end_us = pulse_180_start_us + 2 * pulse_length_us
        record_start_us = pulse_180_end_us + delay_after_p2_us
        record_end_us = record_start_us + record_length_us
        tx_sequence = (
            np.array(
                [
                    pulse_90_start_us,
                    pulse_90_end_us,
                    pulse_180_start_us,
                    pulse_180_end_us,
                ]
            ),
            np.array([1, 0, 1, 0]),
        )
        rx_sequence = np.array([record_start_us, record_end_us])
        return cls(tx_sequence, rx_sequence)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NMRSequence):
            try:
                return np.allclose(self.tx_sequence, other.tx_sequence) and np.allclose(
                    self.rx_sequence, other.rx_sequence
                )
            except ValueError:
                return False
        else:
            return NotImplemented


class Spectrometer:
    """Class containing the basic information on an experiment (mixing frequencies,
    sampling rate, server information, ...) as well as managing the connection state of
    the spectrometer.

    Instantiate this class with the required parameters and then use the `send_sequence()` or
    `send_sequences()` functions to perform experiments (i.e. send pulses and acquire a signal).
    """

    def __init__(
        self,
        tx_freq: float,
        rx_freq: float | None = None,
        sample_rate: float = 320e3,
        server_config: ConnectionSettings | None = None,
    ) -> None:
        """Create new basic experiment configuration and connect to the spectrometer.

        After instantiation pulse sequence(s) can be send with the respective `send_...()`
        functions.

        Reminder: Since this class manages the connection to the spectrometer, only one
        `PulseExperiment` can be created per spectrometer. Successive instantiations will fail.

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
        server_cfg = server_config if server_config else ConnectionSettings()
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
                f"{1/server_cfg.fpga_clock_freq}s. Thus the next closest multiple would be "
                f"{server_cfg.fpga_clock_freq/np.round(server_cfg.fpga_clock_freq/sample_rate)}Hz."
            )
            raise ValueError(msg)

        self.tx_freq = tx_freq
        self.rx_freq = rx_freq
        self.sample_rate = sample_rate
        self.server_config = server_cfg
        self.socket = None

    def send_sequence(
        self, sequence: NMRSequence, *, debug: bool = False
    ) -> npt.NDArray:
        """Send the given excitation pulse sequence to the probe and receive a signal for
        `rx_length_us` after the end of the pulse.

        Needs to be connected to a spectrometer through the `connect()` method

        Args:
            sequence (PulseSequence): Event sequence describing a pulse experiment. For details see
            `PulseSequence` documentation
            rx_length_us (float): Length in us to receive data for

        Returns:
            tuple[npt.NDArray, float]: Flat array with the received (complex) data in time domain after
            QI-demodulation/downconversion, CIC-filter and sampling.
        """
        if not self.socket:
            msg = "Call `connect()` before making any calls on this object"
            raise ConnectionError(msg)

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

        # Move all timestamps 10us to the future to make room for RX gate switching as
        # timestamps need to be positive
        tx_t = sequence.tx_sequence[0] + 10

        # Find pulse edge indexes
        tx_p = np.concatenate(([0], sequence.tx_sequence[1]))
        pulse_start_idx = np.nonzero((tx_p[:-1] == 0) & (tx_p[1:] != 0))[0]
        pulse_end_idx = np.nonzero((tx_p[:-1] != 0) & (tx_p[1:] == 0))[0]

        # Find pulse and recording start and end times
        pulse_starts = tx_t[pulse_start_idx]
        pulse_ends = tx_t[pulse_end_idx]

        # Don't transmit while switching or transmit gate is off!
        tx_gate_on = pulse_starts - 1
        tx_gate_off = pulse_ends + 1
        tx_gate_sequence = _merge_overlapping_ranges(tx_gate_on, tx_gate_off).flatten()

        # Switch rx_gate whenever we receive
        rx_gate_sequence = sequence.rx_sequence

        exp.add_flodict(
            {
                "tx0": (tx_t, sequence.tx_sequence[1]),
                "tx_gate": (
                    tx_gate_sequence,
                    np.resize([1, 0], len(tx_gate_sequence)),
                ),
                "rx0_en": (
                    sequence.rx_sequence,
                    np.resize([1, 0], len(sequence.rx_sequence)),
                ),
                "rx_gate": (
                    rx_gate_sequence,
                    np.resize([1, 0], len(rx_gate_sequence)),
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
            data = self.send_sequence(sequence)
            fids.append(data)
            logger.info("Sleeping for %ss...", repetition_time_s)
            time.sleep(repetition_time_s)

        return fids

    def connect(self) -> None:
        """Connect to spectrometer server (i.e. the MaRCoS server running on the RedPitaya)"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5s timeout for all commands
        sock.connect(self.server_config.socket_config)
        self.socket = sock

    def disconnect(self) -> None:
        """Shutdown the connection (by first sending a FIN/EOF to the server) and then try to close
        the socket.

        Note that the OS level socket might not be deallocated if other processes still
        have an open handle to it.
        """
        # https://docs.python.org/3/howto/sockets.html#disconnecting
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except OSError:
            logger.info("Error closing the socket. Maybe it is already closed?")

    def __del__(self) -> None:
        self.disconnect()


class Server:
    def __init__(self, ip_address: IPv4Address | IPv6Address | None = None) -> None:
        """Create new connection the the RedPitaya for managing the server

        Args:
            ip_address (IPv4Address | IPv6Address, optional): IP address of the spectrometer. If
            None, tries to load address from config. Defaults to None.
            port (int, optional): Network Port of the spectrometer. If None, tries to load the port
            from config. Defaults to None.
        """
        self.ip_address = (
            ip_address
            if ip_address
            else ipaddress.ip_address(config["server"]["ip_address"])
        )

    def flash_fpga(self, red_pitaya_model: str = "rp-122") -> None:
        if self.is_running():
            logger.warning("MaRCoS server is already running! Stopping server...")
            self.stop()

        with Connection(
            host=str(self.ip_address), user="root", connect_timeout=5
        ) as conn:
            if _file_exists(conn, "/opt/redpitaya/version.txt"):
                # Standard RedPitaya Image
                _transfer_file(
                    from_url=f"{MARCOS_EXTRAS_URL}/marcos_fpga_{red_pitaya_model}.bit",
                    to_conn=conn,
                    to_file="/tmp/marcos_fpga.bit",  # noqa: S108
                )
                # Flash the bitstream
                conn.run("cat /tmp/marcos_fpga.bit > /dev/xdevcfg")
                conn.run("rm /tmp/marcos_fpga.bit")
            else:
                # Ocra image
                _transfer_file(
                    from_url=f"{MARCOS_EXTRAS_URL}/marcos_fpga_{red_pitaya_model}.bit.bin",
                    to_conn=conn,
                    to_file="/lib/firmware/marcos_fpga.bit.bin",
                )
                _transfer_file(
                    from_url=f"{MARCOS_EXTRAS_URL}/marcos_fpga_{red_pitaya_model}.dtbo",
                    to_conn=conn,
                    to_file="/lib/firmware/marcos_fpga.dtbo",
                )
                if _dir_exists(conn, "/sys/kernel/config/device-tree/overlays/full"):
                    conn.run("rmdir /sys/kernel/config/device-tree/overlays/full")
                conn.run("echo 0 > /sys/class/fpga_manager/fpga0/flags")
                conn.run("mkdir /sys/kernel/config/device-tree/overlays/full")
                conn.run(
                    "echo -n 'marcos_fpga.dtbo' > /sys/kernel/config/device-tree/overlays/full/path"
                )

    def setup(self) -> None:
        if self.is_running():
            logger.warning("MaRCoS server is already running! Stopping server...")
            self.stop()

        with Connection(
            host=str(self.ip_address), user="root", connect_timeout=5
        ) as conn:
            now = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S,%f000%z")
            now = f"{now[:-2]}:{now[-2:]}"
            conn.run(f"date -Ins -s '{now}'", hide=True)

            _transfer_file(
                from_url=MARCOS_SERVER_URL,
                to_conn=conn,
                to_file="/tmp/marcos_server.zip",  # noqa: S108
            )
            with conn.cd("/tmp"):  # noqa: S108
                conn.run("unzip -o marcos_server.zip", hide=True)
                conn.run("mkdir -p /tmp/marcos_server-master/build")
            with conn.cd("/tmp/marcos_server-master/build"):  # noqa: S108
                conn.run("cmake ../src", hide=True)
                conn.run("make -j2", hide=True)
                conn.run("cp marcos_server ~/")

    def start(self) -> None:
        if self.is_running():
            logger.warning("MaRCoS server is already running! Restarting...")
            self.stop()

        with Connection(
            host=str(self.ip_address), user="root", connect_timeout=5
        ) as conn:
            conn.run("nohup ./marcos_server &>./marcos_server.log </dev/null &")

    def stop(self) -> None:
        if self.is_running():
            with Connection(
                host=str(self.ip_address), user="root", connect_timeout=5
            ) as conn:
                conn.run("pkill marcos_server")
            logger.info("Server stopped")
        else:
            logger.warning("Server is not running! Skipping...")

    def is_running(self) -> bool:
        with Connection(
            host=str(self.ip_address), user="root", connect_timeout=5
        ) as conn:
            return bool(conn.run("pgrep marcos", warn=True, hide=True).stdout.strip())


def _merge_overlapping_ranges(starts: list, ends: list) -> npt.NDArray:
    p = list(zip(sorted(starts), sorted(ends), strict=True))

    ind = np.where(np.diff(np.array(p).flatten()) <= 0)[0]
    ind = ind[ind % 2 == 1]  # this is needed for cases when x_i = y_i
    return np.delete(p, [ind, ind + 1]).reshape(-1, 2)


def _transfer_file(from_url: str, to_conn: Connection, to_file: str) -> None:
    with request.urlopen(from_url) as response:  # noqa: S310
        with tempfile.TemporaryFile() as tmp_file:
            shutil.copyfileobj(response, tmp_file)
            to_conn.put(tmp_file, remote=to_file)


def _file_exists(conn: Connection, file: str) -> bool:
    return not conn.run(f"[ -f {file} ]", hide=True, warn=True).exited


def _dir_exists(conn: Connection, directory: str) -> bool:
    return not conn.run(f"[ -d {directory} ]", hide=True, warn=True).exited
