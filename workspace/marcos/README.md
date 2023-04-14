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

#### Running the `marga` simulator

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

### Red Pitaya

- Login: root
- Password: root

#### Flash the custom marcos Yocto image

1. (This is mostly [following the wiki tutorial](https://github.com/vnegnev/marcos_extras/wiki/guide_setting_marcos_up))
2. [Download the SD Card image](https://drive.google.com/file/d/1Kz3a7ylPrvh3pxZz5EkwARKeRLj5R6fp/view?usp=sharing)
3. Extract: `tar -xvf sdimage-bootpart-202004030120-mmcblk0.direct.tar.bz2`
4. Write to SD-card `sudo dd if=sdimage-bootpart-202004030120-mmcblk0.direct of=/dev/mmcblk0 bs=1M status=progress && sync`
5. Put the micro SD-Card into the RedPitaya

#### Alternatively: Flash the standard RedPitaya Image

1. Download the latest image for the RP 122-16 from [the official Red Pitaya homepage](https://redpitaya.readthedocs.io/en/latest/quickStart/SDcard/SDcard.html)
2. Extract it: `cd ~/Downloads` and then `unzip SDRlab_122-16_OS_1.04-11_stable.img.zip`
3. Write to SD-card `sudo dd if=SDRlab_122-16_OS_1.04-11_stable.img of=/dev/mmcblk0 bs=1M status=progress && sync`
4. Put the micro SD-Card into the RedPitaya

#### Connect through serial
1. Connect the middle port (left micro-USB port) of the Red Pitaya to the laptop
2. Install `tio` with `sudo dnf install tio` then run `tio /dev/ttyUSB0` (or use `minicom`/`PuTTY`)
3. You've got a shell!
4. Login is `root`. Password if promted is `root` as well.

To configure a static IP (here: `192.168.1.100`) for the RedPitaya change the line
```bash
iface eth0 inet dhcp
```
to
```bash
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    network 192.168.1.0
    gateway 192.168.1.1
```

#### Connect through Ethernet
> Note: By default, the RedPitaya needs a DHCP server for configuration. For the below to work you need to configure the RedPitaya's IP statically through the USB serial connection first (see above).
1. Connect the Ethernet cable directly to the laptop
2. Configure the Laptop ethernet interface statically to
    - IP: 192.168.1.1
    - Subnetmask: 255.255.255.0
    - Gateway: 192.168.1.1
3. Use ssh to connect to the Red Pitaya: `ssh root@192.168.1.100`

#### Start the server

From the laptop/console get the `marcos_extra` repo and execute:
```bash
./marcos_setup.sh 192.168.1.100 rp-122
./copy_bitstream.sh 192.168.1.100
```

Then simply run
```bash
./marcos_server
```

which you then find in the home directory of the Red Pitaya after logging in through SSH. Or execute it directly:
```bash
ssh root@192.168.1.100 "~/marcos_server"
```

#### Test the server

After starting the server (see above) you can test the server by executing
```bash
python test_server.py
```
on the Console/Laptop from the `marcos_client` repository. All tests should pass.

The script
```bash
python test_noise.py
```
can be used to generate some pulses and look at them through an oscilloscope.

#### SD-Card usage

Currently there are three micro sd cards in use:
| micro SD Card                   | Image                                                                                                         | User | Password |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---- | -------- |
| SanDisk Ultra (red/white, 16GB) | RedPitaya standard                                                                                            | root | root     |
| SanDisk (black, 16GB)           | MaRCoS image (Ocra Yocto Image)                                                                               | root | root     |
| NoName (black, 2GB)             | ["Pavel Denim" - Red Pitaya for Pulsed NMR](http://pavel-demin.github.io/red-pitaya-notes/pulsed-nmr-122-88/) | root | changeme |

## Misc

To backup an SD card, use the following command (with admin rights, so probably prefix `sudo`):
```bash
dd if=/dev/mmcblk0 status=progress bs=4M | gzip  > sd_card.img.gz
```
