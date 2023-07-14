import logging

import matplotlib.pyplot as plt
import numpy as np
import nmrglue as ng

logger = logging.getLogger(__name__)


from marcos import Experiment


def send_simple_pulse() -> None:
    sample_freq_MHz = 0.32
    sample_time_us = 1 / sample_freq_MHz
    # Send with 25.01MHz on tx0, tx1, set third lo to 25 MHz
    # rx_lo=2 -> set receive lo for both channels to third (i.e. 25MHz lo)
    exp = Experiment(lo_freq=(25.09, 25.09, 25.00), rx_lo=2, rx_t=sample_time_us)

    tx_start_us = 100
    tx_length_us = 9
    tx_power = 1  # %

    tx_end_us = tx_start_us + tx_length_us

    # Make sure to not send a pulse while switching the gate
    tx_gate_pre_us = 1
    tx_gate_post_us = 1

    tx_rx_delay_us = 35  # must be >= tx_gate_post_us

    rx_start_us = tx_end_us + tx_rx_delay_us
    rx_length_us = 10_000
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
    _, tx_axes = plt.subplots(4, 1, figsize=(12, 8), layout="constrained")
    exp.plot_sequence(axes=tx_axes)

    # Execute the sequence
    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)

    # Print msgs
    print(rxd)
    print(msgs)

    # Plot results
    rx_mV_factor = 250 / 16.370  # Measured Estimate!
    time_rx0_us = np.arange(0, rxd["rx0"].size) * sample_time_us
    _, rx_axes = plt.subplots(
        3, 1, figsize=(12, 8), sharex="all", sharey="all", layout="constrained"
    )
    rx_axes[0].set_title("RX 0 I")
    rx_axes[0].set_ylabel("Voltage [mV]")
    rx_axes[0].plot(time_rx0_us, rxd["rx0"].real * rx_mV_factor)
    rx_axes[1].set_title("RX 0 Q")
    rx_axes[1].set_ylabel("Voltage [mV]")
    rx_axes[1].plot(time_rx0_us, rxd["rx0"].imag * rx_mV_factor)
    rx_axes[2].set_title("RX 0 Absolute")
    rx_axes[2].set_ylabel("Voltage [mV]")
    rx_axes[2].plot(time_rx0_us, np.absolute(rxd["rx0"]) * rx_mV_factor)
    rx_axes[2].set_xlabel("Time within RX 0 Window [$\mu$s]")

    # data = ng.proc_base.zf_size(data, 32768)    # zero fill to 32768 points, fft is faster with power of 2
    data = ng.proc_base.fft(rxd["rx0"])  # Fourier transform
    data = ng.proc_base.ps(data, p0=180.0)  # phase correction
    data = ng.proc_base.di(data)  # discard the imaginaries
    data = ng.proc_base.rev(data)  # reverse the data
    freq_fft = np.arange(0, data.size) * sample_freq_MHz * 1e6

    _, fft_axes = plt.subplots(1, 1, figsize=(12, 8), layout="constrained")

    fft_axes.set_title("RX 0 FFT")
    fft_axes.set_ylabel("Amplitude [au]")
    fft_axes.set_xlabel("Frequency [Hz]")
    fft_axes.plot(freq_fft, data)

    plt.show()


if __name__ == "__main__":
    send_simple_pulse()
