#!/usr/bin/env python3
"""Simple script that sends a single classic pulse echo sequence"""

import logging
from pathlib import Path

from spectrometer import FID1D, NMRSequence, Server, Spectrometer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Prepare the spectrometer and send a pulse echo sequence"""

    logger.info("Creating pulse echo sequence...")
    pulse_length_us = 9  # From rabi nutation experiment
    delay_us = 100_000
    record_length = 130e3
    seq = NMRSequence.spin_echo(
        pulse_length_us=pulse_length_us,
        delay_tau_us=delay_us,
        delay_after_p2_us=30,
        record_length_us=record_length,
    )

    logger.info("Setting up spectrometer server...")
    server = Server(ip_address="192.168.1.100")
    server.flash_fpga()
    server.setup()
    server.start()

    logger.info("Connecting to server and sending sequence...")
    spec = Spectrometer(tx_freq=25_089_700)
    spec.connect()
    data = spec.send_sequence(seq)
    spec.disconnect()

    logger.info("Saving FID...")
    fid = FID1D(
        data=data,
        spectral_width=spec.sample_rate,
        carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
        observation_freq=spec.rx_freq,
        label="1H",
        sample="Water",
        pulse=f"spin_echo,length={pulse_length_us}us,delay_tau={delay_us}us,record_length={record_length},sample_rate={spec.sample_rate},probe=andrew",
        spectrometer="magnETHical v0.1",
    )
    timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
    file = (
        Path(__file__).parent.parent
        / f"data/{timestr}-{fid.sample}-{fid.label}-{fid.pulse}.fid"
    )
    fid.to_file(file)
    logger.info("Saved FID to %s", file)


if __name__ == "__main__":
    main()
