import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from sequences.marcos_client import experiment as ex

# dirty hack, cause marcos_client uses direct imports for neighboring files
marcos_client = (Path(__file__).parent / "marcos_client").resolve()
sys.path.append(str(marcos_client))


def my_first_experiment():
    exp = ex.Experiment(lo_freq=5, rx_t=3.125)
    tx0_times = np.array([50, 130])
    tx0_amps = np.array([0.5, 0])

    event_dict = {"tx0": (tx0_times, tx0_amps)}
    exp.add_flodict(event_dict)
    exp.add_flodict({"rx0_en": (np.array([200, 400]), np.array([1, 0]))})

    exp.plot_sequence()
    plt.show()


if __name__ == "__main__":
    my_first_experiment()
