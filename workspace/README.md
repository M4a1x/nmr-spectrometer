# Workspace

Here lies any code/digital work created during the project. This includes design files, measurement data, photographs and more. This is the main folder to be worked in.

For details on the probe, construction see the [README.md](./nmr_probe/README.md) in the [`nmr_probe`](./nmr_probe/) folder.

For details on the control of the MaRCoS software see the [README.md](./marcos/README.md) in the [`marcos`](./marcos/) folder.


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

## Red Pitaya SDRlab 122-16 (STEMlab 122-16)
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