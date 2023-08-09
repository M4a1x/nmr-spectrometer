# Workspace

Here lies any code/digital work created during the project. This includes design files, measurement data, photographs and more. This is the main folder to be worked in.

| Folder                                                      | Description                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [`nmr_probe`](./nmr_probe/)                                 | Probe and Probe construction                                                                                        |
| [`marcos`](./marcos/)                                       | MaRCoS software and control of the spectrometer                                                                     |
| [`32-channel_current_source`](./32-channel_current_source/) | Digitally controllable current source for driving the shims                                                         |
| [`tr_switch`](./tr_switch/)                                 | Transmit/Receive Switch for Switching between High-Power RF impulse transmission and low level FID signal reception |
| [`rx_lna_preamp`](./rx_lna_preamp/)                         | Low-Noise Amplifier for the amplification of the FID signal for the RedPitaya                                       |
| [`tx_power_amp`](./tx_power_amp/)                           | Power Amplifier to amplify the excitation pulse of the RedPitaya                                                    |

## General Setup
```text
+------------+                                            +--------------+
|            |     |\            |\                       | RX/TX Switch |
|            |     | \           | \                      |              |
|         TX |-----|  +----------|  +---------------------|---x  \       |         \ | /
|            |     | /           | /                      |       \      |          \|/
|            |     |/            |/                       |        \     |           |
|            |  ZFL-1000+      ZHL-3A+                    |         \    |           |
| Red Pitaya |                                            |          +---|-----------+
|            |                                            |              |
|            |       /|            /|           /|        |              |
|            |      / |           / |          / |        |              |
|         RX |-----+  |----------+  |---------+  |--------|---x          |
|            |      \ |           \ |          \ |        |              |
|            |       \|            \|           \|        |              |
|            |   ZFL-500LN+     PHA-13LN+   PHA-13LN+     |              |
+------------+                                            +--------------+
```

## Previous NMR Work

- Designing and building a low-cost portable FT-NMR spectrometer in 2019: A modern challenge (Alain Lous-Joseph, Philippe Lesot)
- OpenCore NMR (Kazuyuki Takeda)
- LabTools NMR spectrometer based on RedPitaya
- Pavel Demin's NMR spectrometer
- [Simple Low-Cost Tabletop NMR for chemical-shift-resolution spectra measurements](https://www.sciencedirect.com/science/article/pii/S1090780718301745#b0110). Home-built magnet, 60Hz resolution at 2.45MHz (58.8mT), in a later paper down to 1ppm.

## NMR Spectrometer Target Specifications

In addition to the [thesis description/project proposal](../literature/project_proposal/Master_Thesis_Proposal.pdf) we tried to meet the following specifications. This includes design requirements for the physical setup partially repeated in the various sub-sections in the `workspace` directory. Hardware should be reusable. The end goal would be of type "Bring your own Magnet", i.e. a Red Pitaya SDRLab 122.88, our board and magnet should be enough to do spectroscopy, when building their own probes.

- Larmor Frequency: 25MHz (0.6T)
- RF-field strength: x.xx mT
- pi/2 pulse length: x.xx us

> **TODO**
> Write down NMR target specifications here

In the end, separate modules should be developed for ease of reconfiguration. A nice addition would be a single board, including RX/TX amplifiers, switch and filters on one standard [Eurocard 3U (100mm x 160mm x 1.6mm)](https://en.wikipedia.org/wiki/Eurocard_(printed_circuit_board)) FR4 board, so it can be rack mounted, possibly with the common [DIN 41612](https://en.wikipedia.org/wiki/DIN_41612) (~~STEbus~~, VMEbus) connector at the back end. See also the [ARTIQ/Sinara project](https://github.com/sinara-hw/SiLPA_HL/issues/1).

## Red Pitaya SDRlab 122-16 (STEMlab 122-16)
The ADC of the RedPitaya is specified for an RF input voltage of 0.5Vpp. Its absolute maximum rating is 30VDC and 1Vpp RF (~4dBm). This has been verified by looking at the [used ADC](https://www.analog.com/media/en/technical-documentation/data-sheets/218543f.pdf) and the [RedPitaya Schematic](../../literature/instruments/Customer_Schematics_STEM122-16SDR_V1r1(Series1).PDF). Thus the input has to be protected from the power of the transmit cycle.

The easiest way to do this is to use a TVS diode for clamping the input to safe levels. Unfortunately, this severely degrades the ADCs performance according to [this Analog Devices Application Note](../../literature/instruments/rf-samp-adc-input-protection.pdf). The same AN suggests using [RB851Y](https://www.mouser.com/datasheet/2/348/rb851y-209815.pdf) Schottky diodes for ADC input protection
### Basic Specs
|                    |                           |
| ------------------ | ------------------------- |
| Processor          | DUAL CORE ARM CORTEX A9   |
| FPGA               | FPGA Xilinx Zynq 7020 SOC |
| RAM                | 512 MB (4 Gb)             |
| System Memory      | Micro SD up to 32 GB      |
| Console Connection | Micro USB                 |
| Power Connector    | Micro USB                 |
| Power Consumption  | 5 V, 2 A max              |

### RF Inputs
|                                   |                                       |
| --------------------------------- | ------------------------------------- |
| RF input channels                 | 2                                     |
| Sample rate                       | 122.88 MS/s                           |
| ADC resolution                    | 16 bit                                |
| Input impedance                   | 50 Ohm                                |
| Full scale voltage range          | 0.5 Vpp/-2 dBm                        |
| Input coupling                    | AC                                    |
| Absolute max. Input voltage range | DC max 50 V (AC-coupled) 1 Vpp for RF |
| Input ESD protection              | Yes                                   |
| Overload protection               | DC voltage protection                 |
| Bandwidth                         | 300 kHz - 550 MHz                     |

### RF Outputs
|                         |                                  |
| ----------------------- | -------------------------------- |
| RF output channels      | 2                                |
| Sample rate             | 122.88 MS/s                      |
| DAC resolution          | 14 bit                           |
| Load impedance          | 50 Ohm                           |
| Voltage range           | 0.5 Vpp/ -2 dBm (50 Ohm load)    |
| Short circut protection | N/A, RF transformer & AC-coupled |
| Connector type          | SMA                              |
| Output slew rate        | N/A                              |
| Bandwidth               | 300 kHz - 60 MHz                 |

Next Steps:
1. Build 2x Protection diode blocks with 2x BYS-10 schottky diodes each for input protection (limit power to 4dBm/+-0.5V/1Vpp)