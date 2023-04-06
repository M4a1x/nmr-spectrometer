# MaRCoS

## Setup

### Console / Laptop

The current system uses `Fedora 38 Workstation`, but any modern Linux (recent!) like Ubuntu or Arch would work as well. Fedora was chosen for its extensive support, backing by RedHat, and wide use of its sibling CentOS in the scientific community, while still being more recent and modern with a quick release schedule without the drawbacks of a rolling release system.

After installation of the base system the [MaRCoS client](https://github.com/vnegnev/marcos_client) was set up according to the [tutorial in the wiki](https://github.com/vnegnev/marcos_extras/wiki/tut_set_up_marcos_software), _but_ in a new python (3.11.2) virtual environment as is best practice. An extended C & Electronics group was installed as well do ease development. In short:

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

To activate the Python environment in a terminal and use the installed packages execute (inside the `marcos_pack` folder):
- `source .venv/bin/activate`

#### Run unit tests

- `cd marcos_client`
- `cp local_config.py.example local_config.py`

Set contents to:

```python
ip_address = "localhost"
port = 11111
fpga_clk_freq_MHz = 122.88

grad_board = "gpa-fhdo"

gpa_fhdo_current_per_volt = 2.5
```

Build the marga simulator (independent from above client):

```bash
cd marcos_pack/marga
mkdir build
cd build
cmake ../src
make
```

If you execute `ls` inside the folder now you should see a new executable `marga_sim` which is the simulator!

Now we can run the unit tests against the simulator:

```bash
cd marcos_pack/marcos_client
python test_marga_model.py
```

Getting a `RuntimeWarning: gpafhdo gradient error; [...]`  is fine here.

## Running the `marga` simulator

To run the `marga` simulator a file needs to be allocated in RAM:
```bash
fallocate -l 516KiB /tmp/marcos_server_mem
```

To then run the simulator execute the following, which will start the simulator and dump event output to a `*.csv` file in the same directory:
```bash
cd marcos_pack/marga/build
./marga_sim csv
```

When you then run an experiment from Python `exp.run()` and then close the server e.g. directly after the experiment run with a `exp.close_server(only_if_sim=True)`, the outputted `marga_sim.csv` can be plotted by the `plot_csv.py` script in the `marcos_client`.

```bash
python plot_csv.py ../marga/build/marga_sim.csv
```