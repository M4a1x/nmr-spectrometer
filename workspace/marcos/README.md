# MaRCoS

## Setup

### Console / Laptop

The current system uses `Fedora 38 Workstation`, but any modern Linux (recent!) like Ubuntu or Arch would work as well. Fedora was chosen for its extensive support, backing by RedHat, and wide use of its sibling CentOS in the scientific community, while still being more recent and modern with a quick release schedule without the drawbacks of a rolling release system.

After installation of the base system the [MaRCoS client](https://github.com/vnegnev/marcos_client) was set up according to the [tutorial in the wiki](https://github.com/vnegnev/marcos_extras/wiki/tut_set_up_marcos_software), _but_ in a new python virtual environment as is best practice. An extended C & Electronics group was installed as well do ease development. In short:

#### OS Setup

**Fedora**:
- `sudo dnf group install -q --with-optional "Development Libraries" "Development Tools" "C Development Tools and Libraries" "Electronic Lab"`
**Arch**:
- `sudo pacman -S base-devel verilator cmake`

#### Python environment

- `git clone --recurse-submodules https://github.com/vnegnev/marcos_pack.git`
- `cd marcos_pack`
- `python -m ensurepip`
- `python -m pip install -U pip`
- `python -m venv .venv`
- `python -m install -U numpy scipy matplotlib msgpack`

To activate the python environment in a terminanl and use the installed package execute (inside the `marcos_pack` folder):
- `source .venv/bin/activate`

#### Run unit tests

