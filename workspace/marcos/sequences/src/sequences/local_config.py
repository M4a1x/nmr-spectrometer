# Adapted from vnegnev/marcos_client/local_config.py.example

## IP address: RP address or 'localhost' if emulating a local server.
## Uncomment one of the lines below.
# ip_address = "localhost"
ip_address = "192.168.1.100"

## Port: always 11111 for now
port = 11111

## FPGA clock frequency: uncomment one of the below to configure various
## system behaviour. Right now only 122.88 is supported.
fpga_clk_freq_MHz = 122.88  # RP-122  # noqa: N816
# fpga_clk_freq_MHz = 125.0 # RP-125

## Gradient board: uncomment one of the below to configure the gradient data format
grad_board = "gpa-fhdo"
# grad_board = "ocra1"

## GPA-FHDO current per volt setting (determined by resistors)
gpa_fhdo_current_per_volt = 2.5

## Flocra-pulseq path, for use of the flocra-pulseq library (optional).
## Uncomment the lines below and adjust the path to suit your
## flocra-pulseq location.
# import sys
# sys.path.append('/home/vlad/Documents/mri/flocra-pulseq')
