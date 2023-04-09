import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


from marcos import Experiment


def my_first_experiment():
    exp = Experiment(lo_freq=5, rx_t=3.125)

    exp.add_flodict({"tx0": (np.array([50, 130]), np.array([0.5, 0]))})
    exp.add_flodict({"rx0_en": (np.array([200, 400]), np.array([1, 0]))})

    exp.plot_sequence()
    plt.show()

    # Execute the sequence
    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)


def my_second_experiment():
    exp = Experiment(lo_freq=5, rx_t=3.125)

    event_dict = {
        "tx0": (np.array([50, 130, 200, 360]), np.array([0.5, 0, 0.5j, 0])),
        "tx1": (np.array([500, 700]), np.array([0.2, 0])),
        "rx0_en": (np.array([400, 800]), np.array([1, 0])),
        "rx1_en": (np.array([400, 800]), np.array([1, 0])),
    }
    exp.add_flodict(event_dict)
    exp.plot_sequence()

    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)

    plt.figure()
    plt.plot(np.abs(rxd["rx1"]))
    plt.show()


if __name__ == "__main__":
    # my_first_experiment()
    my_second_experiment()
