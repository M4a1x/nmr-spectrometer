<div align="center">
  <a href="" rel="noopener">
 <img width="25%" height="auto" src="logo.svg" alt="BioNMR Group Logo"></a>
</div>

<div align="center"><h3>Spectrometer</h3></div>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 
  [![License](https://img.shields.io/badge/license-GPL--3.0-orange.svg)](/LICENSE)

</div>

---

<div align="center"> Spectrometer is the Python interface library for the magnETHical NMR spectrometer. Its aim is to make usage of the hardware as simple and convenient as possible.</div>

## 📝 Table of Contents
- [📝 Table of Contents](#-table-of-contents)
- [🧐 About ](#-about-)
- [🏁 Getting Started ](#-getting-started-)
  - [✅ Prerequisites](#-prerequisites)
  - [🔧 Hardware](#-hardware)
  - [🖥️ Software](#️-software)
- [⚙️ Running the tests ](#️-running-the-tests-)
- [🧪 Usage ](#-usage-)
- [⛏️ Built Using ](#️-built-using-)
- [✍️ Authors ](#️-authors-)
- [🎉 Acknowledgements ](#-acknowledgements-)

## 🧐 About <a name = "about"></a>
The magnETHical spectrometer is a low-cost low-field home-made NMR spectrometer developed at ETH Zürich. This project is providing an interface for setting up the spectrometer software on the RedPitaya 122-16 (SDRLab) system, sending and recording pulse sequences.

## 🏁 Getting Started <a name = "getting_started"></a>

### ✅ Prerequisites
We assume you have [built and assembled the necessary hardware](../../hardware/) and that you have a Linux computer in front of you (preferably running a RedHat-flavoured system like RHEL, Fedora, CentOS, ...) that is connected to the RedPitaya through Ethernet (i.e. you know its IP address). 

The RedPitaya should automatically get an IP address assigned by the router (i.e. DHCP is enabled by default). If you connect your laptop directly to the RedPitaya you need to either run your own DHCP server or you need to statically configure the IP address through the serial USB interface of the RedPitaya. If you don't know how, please look at [my MaRCoS documentation](../marcos/README.md#connect-through-serial). You don't need to follow all of the instructions, configuring the IP address is enough to use this software. If you'd like to run your own DHCP server, there are [detailed instructions for Arch available here](https://github.com/vnegnev/marcos_extras/wiki/guide_setting_marcos_up#13a-preparing-a-local-network-vlads-linux-method).

### 🔧 Installation
This library is a regular Python package

### 🖥️ Software
Having built the hardware above the [Python control software]() can be used to capture spectra. See the linked article for a detailed guide on how to set up the software. We recommend a dedicated computer setup to run the experiments.

## ⚙️ Running the tests <a name = "tests"></a>
The simplest test is running marcos test without/with water. measure coil ringing

Explain how to run the automated tests for this system.


## 🧪 Usage <a name="usage"></a>
To record spectra...

How to use the software/hardware. Recomenndations on analysis (Jupyter...)
Add notes about how to use the system.

## ⛏️ Built Using <a name = "built_using"></a>

- Hardware
  - [KiCAD](https://www.kicad.org/) - ECAD for PCB Design
  - [FreeCAD](https://www.freecad.org/) - MCAD for Enclosures
  - [OpenSCAD](https://openscad.org/) - Parametric CAD for the probe
  - [LTSpice](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html) - Simulation of electronic circuits
- Software
  - [MaRCoS](https://github.com/vnegnev/marcos_extras) - Low-level control software for the RedPitaya and FPGA
  - [NumPy](https://numpy.org/)/[SciPy](https://scipy.org/)/[Matplotlib](https://matplotlib.org/) - High-level control software and analysis
- Documentation
  - [LaTeX](https://www.latex-project.org/) - Advanced typesetting system
  - [Sphinx](https://www.sphinx-doc.org) - Beautiful documentation

## ✍️ Authors <a name = "authors"></a>
- [Maximilian Stabel](mailto:mstabel@student.ethz.ch) - Idea & Initial work including Hardware & Software

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- Supervisor
  - [**Takuya Segawa**](https://chab.ethz.ch/forschung/institute-und-laboratorien/LPC/personen/people-details.html?persid=120573) for his supervision and encouragement
- Professors
  - [**Roland Riek**](https://chab.ethz.ch/en/the-department/people/faculty/person-detail.rriek.html) for giving me this opportunity
  - [**Sebastian Kozerke**](https://biomed.ee.ethz.ch/institute/People/person-detail.html?persid=61641) for taking me in as his Master's student
- Support
  - [**Alexander Däpp**](https://ssnmr.ethz.ch/the-group/people/person-detail.html?persid=147372) for his support and patience with the RF hardware
  - [**Tiago Ferreira das Neves**](https://chab.ethz.ch/en/the-department/people/a-z/person-detail.MjU3NzM4.TGlzdC82MDEsLTIxMzAxOTI4MDM=.html) for his electronics support

<div align="center">
  <a href="" rel="noopener">
 <img width="25%" height="auto" src="./logo_bionmr.png" alt="BioNMR Group Logo"></a>
</div>




# Spectrometer

This project contains sequences to send to the marcos_server for NMR experiments.

## Notes

For analysis of later spectra:
- [`POKY`](https://github.com/pokynmr/POKY) is the successor of [SPARKY](https://www.cgl.ucsf.edu/home/sparky) by UCSF and the [`NMRFAM-SPARKY`](https://nmrfam.wisc.edu/nmrfam-sparky-distribution/) distribution
- [`spectrochempy`](https://www.spectrochempy.fr) looks promising (only Bruker, JCAMP, OPUS, OMNIC data)
- `penguins` (reads only Bruker data?)

Other noteworthy data formats:
- [`nmrML`](https://github.com/nmrML/nmrML) open NMR data format. read supported by NMRglue
- [`JCAMP-DX`](http://www.jcamp-dx.org/) Open NMR data format. Read supported by NMRglue