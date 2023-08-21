#!/usr/bin/env python3
"""Small script to record multiple FIDs after single pulses with increasing length"""

import logging
from pathlib import Path

import numpy as np

from spectrometer import FID1D, NMRSequence, Server, Spectrometer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Send series of pulses with increasing length"""

    logger.info("Creating pulse sequences...")
    pulse_lengths_us = np.linspace(1, 180, 90)
    delay_us = 30
    repetition_time_s = 1
    sequences = [
        NMRSequence.simple(
            pulse_length_us=pulse_length_us, delay_us=delay_us, record_length_us=10e3
        )
        for pulse_length_us in pulse_lengths_us
    ]

    logger.info("Setting up spectrometer server...")
    server = Server(ip_address="192.168.1.100")
    server.flash_fpga()
    server.setup()
    server.start()

    logger.info("Connecting to spectrometer server and sending pulse sequences...")
    spec = Spectrometer(tx_freq=25_090_000)
    spec.connect()
    datas = spec.send_sequences(
        sequences=sequences, repetition_time_s=repetition_time_s
    )
    spec.disconnect()

    logger.info("Saving FIDs...")
    for i, data in enumerate(datas):
        fid = FID1D(
            data=data,
            spectral_width=spec.sample_rate,
            carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
            observation_freq=spec.rx_freq,
            label="1H",
            sample="Water",
            pulse=f"one_of_repeated_90_degree_pulses,length={pulse_lengths_us[i]}us,delay={delay_us}us,repetition_time={repetition_time_s}s",
            spectrometer="magnETHical v0.1",
        )
        timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
        file = (
            Path(__file__).parent.parent
            / f"data/{timestr}-{fid.sample}-{fid.label}-rabi-nutation/{timestr}-{fid.sample}-{fid.label}-{fid.pulse}.fid"
        )
        fid.to_file(file)
        logger.info("Saved FID %s/%s", i + 1, len(datas))
        logger.info("Filename: %s", file)
    logger.info("Done. Saved all FIDs.")


if __name__ == "__main__":
    main()
