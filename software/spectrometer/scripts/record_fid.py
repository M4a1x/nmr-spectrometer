#!/usr/bin/env python3
"""Small script to record an FID after a simple single pulse"""

import logging
from pathlib import Path

from spectrometer import FID1D, NMRSequence, Server, Spectrometer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating pulse sequence...")
    pulse_length_us = 9
    delay_us = 25  # Wait for coil to ring down
    record_length=10e3
    seq = NMRSequence.simple(
        pulse_length_us=pulse_length_us, delay_us=delay_us, record_length_us=record_length
    )

    logger.info("Setting up spectrometer server...")
    server = Server(ip_address="192.168.1.100")
    server.flash_fpga()
    server.setup()
    server.start()

    logger.info("Connecting to server and sending sequence...")
    spec = Spectrometer(tx_freq=25_089_900, sample_rate=320e3)  # minimum 30_720, maximum ~122.88e6/27 before FIFOs fill
    spec.connect()
    data = spec.send_sequence(seq)
    spec.disconnect()

    logger.info("Saving FIDs...")
    fid = FID1D(
        data=data,
        spectral_width=spec.sample_rate,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        observation_freq=spec.rx_freq,
        label="1H",
        sample="Water",
        pulse=f"single_90_degree_pulse,length={int(pulse_length_us)}us,delay={int(delay_us)}us,record_length={int(record_length)},sample_rate={int(spec.sample_rate)},probe=andrew",
        spectrometer="magnETHical v0.1",
    )
    time = fid.timestamp.strftime("%Y%m%d-%H%M%S")
    file = (
        Path(__file__).parent.parent
        / f"data/{time}-{fid.sample}-{fid.label}-{fid.pulse}.fid"
    )
    fid.to_file(file)
    logger.info("Saved FID to %s", file)


if __name__ == "__main__":
    main()
