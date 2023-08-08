import numpy as np
import numpy.testing as npt

from spectrometer import Delay, NMRSequence, Pulse, Record


def test_empty():
    # Arrange
    expected_seq = NMRSequence((np.array([]), np.array([])))

    # Act
    seq = NMRSequence.empty()

    # Assert
    assert seq == expected_seq


def test_simple_pulse_sequence():
    NMRSequence.simple()


def test_spin_echo():
    NMRSequence.spin_echo()


def test_custom_pulse_sequence_simple():
    # Arrange
    expected_seq = NMRSequence.simple(pulse_length_us=9, delay_us=5)

    # Act
    seq = NMRSequence.build(
        [
            Pulse(power=1, duration_us=9),
            Delay(duration_us=5),
        ]
    )

    # Assert
    assert seq == expected_seq


def test_custom_pulse_sequence_advanced():
    # TODO: Create CPMG sequence with intermediate recordings/measurements
    # Arrange
    expected_seq = NMRSequence.simple(pulse_length_us=9, delay_us=5)

    # Act
    seq = NMRSequence.build(
        [
            Pulse(power=1, duration_us=9),
            Delay(duration_us=5),
        ]
    )

    # Assert
    assert seq == expected_seq
