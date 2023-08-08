import numpy as np
import pytest

from spectrometer import Delay, NMRSequence, Pulse, Record


def test_empty():
    # Arrange
    expected_seq = NMRSequence((np.array([]), np.array([])), np.array([]))

    # Act
    seq = NMRSequence.empty()

    # Assert
    assert seq == expected_seq


def test_spin_echo_sequence():
    # Arrange
    expected_seq = NMRSequence(
        tx_sequence=(np.array([0, 10, 1010, 1030]), np.array([1, 0, 1, 0])),
        rx_sequence=np.array([1080, 11080]),
    )

    # Act
    seq = NMRSequence.spin_echo(
        pulse_length_us=10,
        delay_tau_us=1_000,
        delay_after_p2_us=50,
        record_length_us=10_000,
    )

    # Assert
    assert seq == expected_seq


def test_simple_sequence():
    # Arrange
    expected_seq = NMRSequence.simple(
        pulse_length_us=9, delay_us=5, record_length_us=10_000
    )

    # Act
    seq = NMRSequence.build(
        [
            Pulse(power=1, duration_us=9),
            Delay(duration_us=5),
            Record(duration_us=10_000),
        ]
    )

    # Assert
    assert seq == expected_seq


def test_custom_pulse_sequence_advanced():
    # Arrange
    expected_seq = NMRSequence(
        tx_sequence=(
            np.array([0, 9, 1009, 1027, 12028, 12046]),
            np.array([1, 0, 1, 0, 1, 0]),
        ),
        rx_sequence=np.array(
            [
                2027,
                12027,
                13046,
                23046,
            ]
        ),
    )

    # Act
    seq = NMRSequence.build(
        [
            Pulse(duration_us=9),
            Delay(duration_us=1_000),
            Pulse(duration_us=18),
            Delay(duration_us=1_000),
            Record(duration_us=10_000),
            Delay(duration_us=1),
            Pulse(duration_us=18),
            Delay(duration_us=1_000),
            Record(duration_us=10_000),
        ]
    )

    # Assert
    assert seq == expected_seq


def test_sequence_parsing():
    # Multiple zero/power pulses, should work
    NMRSequence(
        tx_sequence=(np.array([1, 5, 7, 9, 10, 15]), np.array([1, 0, 0, 1, 1j, 0])),
        rx_sequence=np.array([6, 8, 16, 20]),
    )

    # Overlap, should raise
    with pytest.raises(ValueError) as excinfo:
        NMRSequence(
            tx_sequence=(np.array([1, 5]), np.array([1, 0])),
            rx_sequence=np.array([5, 10]),
        )

    assert "simultaneously" in str(excinfo.value)
