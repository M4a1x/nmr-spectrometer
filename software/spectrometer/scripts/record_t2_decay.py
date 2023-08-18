"""Small script to record the T2 decay through multiple classic spin echos"""
#!/usr/bin/env python3

import logging

import numpy as np

from spectrometer import FID1D, NMRSequence, Server, Spectrometer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Send multiple separate classic spin echos with increasing delay"""

    logger.info("Creating pulse sequences...")
    delays_us = np.linspace(100, 300, 100)
    pulse_length_us = 9
    repetition_time_s = 5
    sequences = [
        NMRSequence.spin_echo(
            pulse_length_us=pulse_length_us,
            delay_tau_us=delay_us,
            delay_after_p2_us=delay_us / 2,
            record_length_us=10_000,
        )
        for delay_us in delays_us
    ]

    logger.info("Setting up spectrometer server...")
    server = Server(ip_address="192.168.1.100")
    server.flash_fpga()
    server.setup()
    server.start()

    logger.info("Connecting to spectrometer server and sending pulse sequences...")
    spec = Spectrometer(tx_freq=25_090_230)
    datas = spec.send_sequences(
        sequences=sequences, repetition_time_s=repetition_time_s
    )

    logger.info("Saving FIDs...")
    for i, data in enumerate(datas):
        fid = FID1D(
            data=data,
            spectral_width=spec.sample_rate,
            carrier_freq=0.0,  # Offset between rx_freq and magnet resonance freq. Needs to be calibrated
            observation_freq=spec.rx_freq,
            label="1H",
            sample="Water",
            pulse=f"one_of_repeated_spin_echoes,length={pulse_length_us}us,delay_tau={delays_us[i]}us,repetition_time={repetition_time_s}s",
            spectrometer="magnETHical v0.1",
        )
        timestr = fid.timestamp.strftime("%Y%m%d-%H%M%S")
        file = f"data/{timestr}-{fid.sample}-{fid.label}-t2-decay/{timestr}-{fid.sample}-{fid.label}-{fid.pulse}.fid"
        fid.to_file(file)
        logger.info("Saved FID %s/%s", i + 1, len(datas))
        logger.info("Filename: %s", file)
    logger.info("Done. Saved all FIDs.")


if __name__ == "__main__":
    main()
