<div align="center">
  <a href="" rel="noopener">
 <img width="25%" height="auto" src="logo.svg" alt="magnETHical logo depicting the magnet"></a>
</div>

<div align="center"><h3>Spectrometer</h3></div>

<div align="center">

  [![status][status-badge]]() 
  [![python - version][python-badge]][python]
  [![project - hatch][hatch-badge]][hatch]
  [![linting - Ruff][ruff-badge]][ruff]
  [![code style - Black][black-badge]][black]
  [![types - Mypy][mypy-badge]][mypy]
  [![License][license-badge]][license]

</div>

---

<div align="center"> Spectrometer is the Python interface library for the magnETHical NMR spectrometer. Its aim is to make usage of the hardware as simple and convenient as possible.</div>

## 📝 Table of Contents
- [📝 Table of Contents](#-table-of-contents)
- [🧐 About ](#-about-)
- [🏁 Getting Started ](#-getting-started-)
  - [✅ Prerequisites](#-prerequisites)
  - [🔧 Installation](#-installation)
    - [Python \& Git](#python--git)
    - [Virtual Environment](#virtual-environment)
      - [Manual environment](#manual-environment)
      - [Automatic creating using `Hatch`](#automatic-creating-using-hatch)
    - [Spectrometer Packet](#spectrometer-packet)
- [⚙️ Running the tests ](#️-running-the-tests-)
- [🧪 Usage ](#-usage-)
- [⛏️ Built Using ](#️-built-using-)
- [✍️ Authors ](#️-authors-)
- [Notes](#notes)

## 🧐 About <a name = "about"></a>
The magnETHical spectrometer is a low-cost low-field home-made NMR spectrometer developed at ETH Zürich. This project is providing an interface for setting up the spectrometer software on the RedPitaya 122-16 (SDRLab) system, sending and recording pulse sequences.

## 🏁 Getting Started <a name = "getting_started"></a>

### ✅ Prerequisites
We assume you have [built and assembled the necessary hardware](../../hardware/) and that you have a Linux computer in front of you (preferably running a RedHat-flavoured system like RHEL, Fedora, CentOS, ...) that is connected to the RedPitaya through Ethernet (i.e. you know its IP address).

The RedPitaya should automatically get an IP address assigned by the router (i.e. DHCP is enabled by default). If you connect your laptop directly to the RedPitaya you need to either run your own DHCP server or you need to statically configure the IP address through the serial USB interface of the RedPitaya. If you don't know how, please look at [my MaRCoS documentation](../marcos/README.md#connect-through-serial). You don't need to follow all of the instructions, configuring the IP address is enough to use this software. If you'd like to run your own DHCP server, there are [detailed instructions for Arch available here](https://github.com/vnegnev/marcos_extras/wiki/guide_setting_marcos_up#13a-preparing-a-local-network-vlads-linux-method).

### 🔧 Installation
This library is a regular Python package and can be installed as such. Below you can find an opinionated step-by-step guide on how to set up a Python virtual environment, install the library and set up the spectrometer.

#### Python & Git

First step is to install Python on your system. This repository requires at least Python version 3.10 at the moment. If you're running Linux Python, should already be installed on your system. If it isn't, or if the version is too low it can be installed through the package manager of your Python distribution.

**Fedora**
```bash
$> sudo dnf install python3 git
```

**Ubuntu**
```bash
$> sudo apt install python3 git
```

**Windows**
For Windows you need to go to [the official Python homepage](https://www.python.org/downloads/) and download it from there. Make sure to check "Add the executable to PATH" in the installer. Other than that, accept the recommended defaults if you're unsure.

> **Note**  
> I don't recommend installing Python through the Microsoft Store. Due to packaging and sandboxing weird issues can crop up.

Git can be downloaded from [the official git-scm.com](https://git-scm.com/download/win) website as well. Simply download the appropriate installer for your system (nowadays probably 64bit), execute the downloaded binary and follow the instructions.

#### Virtual Environment

After installation of Python you should create a virtual environment for your project (if you haven't already). This encapsulates the packages and version from the rest of the system to make sure that e.g. a system update doesn't break your project. There are two main ways on going about this: manual creation or using a package manager. I recommend the former for scripts and "to try stuff" and the latter if you're creating your own package.

##### Manual environment
Open a terminal of your choice. In Linux this is often `Terminal`, `urxvt`, `Alacritty`, ... In Windows this is often `Powershell`, `Terminal` (if you installed `Terminal` from the Microsoft Store), or `cmd`. Try looking for it in your search bar (by pressing the Windows key and typing the word).

Now use `cd` to go to the folder you'd like to create your virtual environment in ad create it using Python:
```bash
$> cd ~
$> mkdir myproject
$> cd myproject
$> python3 -m venv .venv
```
This creates a hidden folder named `.venv` inside a new `myproject` folder and initializes your virtual environment.

To activate the virtual environment you need to execute the activation script.
**Linux**
```bash
$> source .venv/bin/activate
```

**Windows**
```bash
$> .venv/bin/activate.ps1     (for powershell)
$> .venv/bin/activate.bat     (for cmd)
```
> **Note**
> If you're using `Powershell` you might have to change the execution policy on your machine. The instructions on how to do that are printed, if the above command fails.

##### Automatic creating using `Hatch`
[Hatch](https://hatch.pypa.io/latest/) is the new standard package manager in Python. It is built on top of `pip` (which installs a package) to automatically figure out dependencies and manage virtual environments. To use it you first need to install it for the current user with `pip`:
```bash
$> python3 -m pip install hatch
```

With pip installed you can now go and create a new project somewhere you like. For example
```bash
$> cd ~
$> hatch new myproject
$> cd myproject
```

`Hatch` then creates a prefilled folder structure for your packet. Hatch always updates the current environment, if something changes in your configuration. All configuration options for your packet can be found inside the `pyproject.toml`. Look e.g. for the `dependencies`.

To activate the virtual environment in your terminal, simply run
```bash
$> hatch shell
```

For other commands, please refer to the [Hatch documentation](https://hatch.pypa.io/latest/intro/).

#### Spectrometer Packet
To install this project as a package you need to clone it to your local hard drive. Advanced users can do a partial clone, but I recommend a simple full clone. In the same directory as your project (i.e. `myproject` if you followed above) execute
```bash
$> git clone https://gitlab.ethz.ch/mstabel/nmr-spectrometer
```
To be able to use the `spectrometer` library in your project you now need to install it inside the virtual environment. Assuming you already activated it you can simply run pip on the corresponding directory:
```bash
$> python3 -m pip install ./nmr-spectrometer/software/spectrometer
```

If you're using hatch you can alternatively add it as a dependency to the `pyproject.toml` by adding the following line to your dependencies
```toml
dependencies = [
  ...
  spectrometer @ {root:uri}/nmr-spectrometer/software/spectrometer
  ...
]
```
The next time you run a hatch command, it will automatically update the virtual environment for you, you can force this ahead of time by e.g. running
```bash
$> hatch run true
```

If everything worked and you're inside the virtual environment you should be able to execute
```bash
$> magnethical --version
magnETHical v0.1.0
```

Congrats! The spectrometer control library is now installed!
## ⚙️ Running the tests <a name = "tests"></a>
The simplest test is running marcos test without/with water. measure coil ringing

Explain how to run the automated tests for this system.


## 🧪 Usage <a name="usage"></a>
To record spectra...

How to use the software/hardware. Recomenndations on analysis (Jupyter...)
Add notes about how to use the system.

## ⛏️ Built Using <a name = "built_using"></a>

  - [MaRCoS](https://github.com/vnegnev/marcos_extras) - Low-level control software for the RedPitaya and FPGA
  - [NumPy](https://numpy.org/)/[SciPy](https://scipy.org/)/[Matplotlib](https://matplotlib.org/) - High-level control software and analysis
  - [Sphinx](https://www.sphinx-doc.org) - Beautiful documentation

## ✍️ Authors <a name = "authors"></a>
- [Maximilian Stabel](mailto:mstabel@student.ethz.ch) - Idea & Initial work including Hardware & Software

## Notes

For analysis of later spectra:
- [`POKY`](https://github.com/pokynmr/POKY) is the successor of [SPARKY](https://www.cgl.ucsf.edu/home/sparky) by UCSF and the [`NMRFAM-SPARKY`](https://nmrfam.wisc.edu/nmrfam-sparky-distribution/) distribution
- [`spectrochempy`](https://www.spectrochempy.fr) looks promising (only Bruker, JCAMP, OPUS, OMNIC data)
- `penguins` (reads only Bruker data?)

Other noteworthy data formats:
- [`nmrML`](https://github.com/nmrML/nmrML) open NMR data format. read supported by NMRglue
- [`JCAMP-DX`](http://www.jcamp-dx.org/) Open NMR data format. Read supported by NMRglue


[status-badge]: https://img.shields.io/badge/status-active-success.svg
[python-badge]: https://img.shields.io/badge/python->=3.7-blue
[python]: https://www.python.org/downloads/
[hatch]: https://github.com/pypa/hatch
[hatch-badge]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[ruff]: https://github.com/charliermarsh/ruff
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json
[black]: https://github.com/psf/black
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[mypy]: https://github.com/python/mypy
[mypy-badge]: https://img.shields.io/badge/types-Mypy-blue.svg
[license-badge]: https://img.shields.io/badge/license-GPL--3.0-orange.svg
[license]: /LICENSE