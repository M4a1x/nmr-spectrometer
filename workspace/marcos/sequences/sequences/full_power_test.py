import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


from marcos import Experiment


def test_all_outputs() -> None:
    sample_freq_MHz = 0.32
    sample_time_us = 1 / sample_freq_MHz
    # Send with 25.01MHz on tx0, tx1, set third lo to 25 MHz
    # rx_lo=2 -> set receive lo for both channels to third (i.e. 25MHz lo)
    exp = Experiment(lo_freq=(25.01, 25.01, 25), rx_lo=2, rx_t=sample_time_us)

    exp.add_flodict(
        {"tx0": (np.array([10000, 20000, 30000, 40000]), np.array([1, 0, 1j, 0]))}
    )
    exp.add_flodict(
        {"tx1": (np.array([50000, 60000, 70000, 80000]), np.array([1, 0, 1j, 0]))}
    )
    exp.add_flodict({"rx0_en": (np.array([0, 90000]), np.array([1, 0]))})
    exp.add_flodict({"rx1_en": (np.array([0, 90000]), np.array([1, 0]))})

    # Plot sequence (doesn´t show yet)
    _, tx_axes = plt.subplots(4, 1, figsize=(12, 8), sharex="col", layout="constrained")
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
    time_rx1_us = np.arange(0, rxd["rx1"].size) * sample_time_us
    _, rx_axes = plt.subplots(3, 2, figsize=(12, 8), sharex="col", layout="constrained")
    rx_axes[0][0].set_title("RX 0 I")
    rx_axes[0][0].set_ylabel("Voltage [mV]")
    rx_axes[0][0].plot(time_rx0_us, rxd["rx0"].real * rx_mV_factor)
    rx_axes[1][0].set_title("RX 0 Q")
    rx_axes[1][0].set_ylabel("Voltage [mV]")
    rx_axes[1][0].plot(time_rx0_us, rxd["rx0"].imag * rx_mV_factor)
    rx_axes[2][0].set_title("RX 0 Absolute")
    rx_axes[2][0].set_ylabel("Voltage [mV]")
    rx_axes[2][0].plot(time_rx0_us, np.absolute(rxd["rx0"]) * rx_mV_factor)
    rx_axes[2][0].set_xlabel("Time within RX 0 Window [$\mu$s]")
    rx_axes[0][1].set_title("RX 1 I")
    rx_axes[0][1].set_ylabel("Voltage [mV]")
    rx_axes[0][1].plot(time_rx1_us, rxd["rx1"].real * rx_mV_factor)
    rx_axes[1][1].set_title("RX 1 Q")
    rx_axes[1][1].set_ylabel("Voltage [mV]")
    rx_axes[1][1].plot(time_rx1_us, rxd["rx1"].imag * rx_mV_factor)
    rx_axes[2][1].set_title("RX 1 Absolute")
    rx_axes[2][1].set_xlabel("Time within RX 1 Window [$\mu$s]")
    rx_axes[2][1].set_ylabel("Voltage [mV]")
    rx_axes[2][1].plot(time_rx1_us, np.absolute(rxd["rx1"]) * rx_mV_factor)
    plt.show()


if __name__ == "__main__":
    test_all_outputs()
