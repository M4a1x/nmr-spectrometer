import argparse
import logging
from pathlib import Path

from marcos.local_config import reload_config

from spectrometer import Server
from spectrometer.__about__ import __version__

logger = logging.getLogger(__name__)


def main():
    args = _parse_args()

    # Verbosity
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)s> %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    logger.info(
        "Logging level set to %s", logging.getLevelName(logger.getEffectiveLevel())
    )

    # Configuration file
    if args.config:
        reload_config([args.config.resolve()])

    # Commands
    match args.command:
        case "flash_fpga":
            Server(ip_address=args.ip, port=args.port).flash_fpga()
        case "setup":
            Server(ip_address=args.ip, port=args.port).setup()
        case "start":
            Server(ip_address=args.ip, port=args.port).start()
        case "stop":
            Server(ip_address=args.ip, port=args.port).stop()
        case "is_running":
            Server(ip_address=args.ip, port=args.port).is_running()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI Client Interface for the magnETHical spectrometer"
    )

    # some default stuff
    parser.add_argument(
        "--version",
        action="version",
        version=f"magnETHical v{__version__}",
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="count", default=0
    )
    parser.add_argument(
        "-c",
        "--config",
        help="path to the *.toml configuration file",
        metavar="local_config.toml",
        type=Path,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port of the spectrometer server",
        default=11111,
    )
    parser.add_argument(
        "-i",
        "--ip",
        help="IP address of the spectrometer",
    )

    parser.add_argument(
        "command",
        help="Command to send to the server",
        choices=["flash_fpga", "setup", "start", "stop", "is_running"],
    )

    return parser.parse_args()
