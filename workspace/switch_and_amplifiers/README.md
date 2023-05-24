# Amplifier

We need two amplifiers for the NMR spectrometer: A gain stage for the transmit path and a low noise amplifier (LNA) for the receive path. Both are connected between the TX/RX switch and the Red Pitaya in their respective paths.

## Circuit Diagram
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

## TX Power Amplifier
Transmit power is expected to be in the area of Watts (Louis-Joseph and Leot (2022)). The max. TX power of the Bruker Fourier 80 is 5W (37dBm) as well. Thus a single amplifier is often not enough and a multi-stage approach is preferable. The RedPitaya maximum output is -2dBm or 0.5Vpp thus 32dB to 39dB amplification would be required.

Previous Work/References:
- The PHA-202+ (30MHZ-2.7GHz) used in a [design in the ETH Quantum Optics Group](https://www.changpuak.ch/electronics/PHA-202+Amplifier.php). Seems to work well down to 2MHz! Probably the best option. Includes Specifics for heatsink, case and PCB. Originally found in the [ARTIQ/Sinara SiLPA discussion](https://github.com/sinara-hw/SiLPA_HL/issues/1) (see below) was well evaluated for its capabilities, there were concerns about temperature stability and praise for ease of use. went with [QPB8808](https://www.qorvo.com/products/p/QPB8808) in the end but need 1.5:1 balun
- [Interesting general article about RF Power amps in NMR](http://www.cpcamps.com/introduction-to-nmr-mri-amplifiers.html)
- [IEEE Paper on how to build an RF power amp for NMR (10-25MHz)](https://ieeexplore.ieee.org/document/5163353)
- [The Stone Zone Blog post about using an IRF510 Mosfet with 2n2222 push-pull preamp](http://thestone.zone/radio/2020/12/13/multi-watt-amplifier.html) for a few Watt amplifier (up to 12W?) [here's a kicad board on github with the IRF510](https://github.com/paulh002/IRF510-rf-amplifier). This transistor seems to be quite popular with HAM people. [Another KiCAD project here](https://github.com/thaaraak/IRF510-Amplifier-v2) with a [circuit walkthrough on youtube](https://www.youtube.com/watch?v=D4UhOmum_oU)
- [HAM Radio Amplifier based on IRF510](https://github.com/kholia/HF-PA-v6), [another project based on the same transistor](https://github.com/paulh002/IRF510-rf-amplifier)
- [The Stone Zone Blog post about using "real" RF Transistors, the 2SK3475 and 2SK3476 for a few Watt amplifier](http://thestone.zone/radio/2021/06/05/power-amplifier.html)
- [The Stone Zone Blog post about the 2sc573 transistor](http://thestone.zone/radio/2022/12/20/2sc573-testing.html) seems to work well for ~2W, but only preliminary testing
- [OpenCore NMR](https://reader.elsevier.com/reader/sd/pii/S1090780708000670?token=C091614A806EFA2BEE0FBD33618073B2E48461C188AAA27B69640A102C862D004694C98189A10EBBDE6AD556E4D1E2EC&originRegion=eu-west-1&originCreation=20230510092722) uses a low pass filter before transmission
- [OpenCore NMR compact educational system](https://www.sciencedirect.com/science/article/pii/B9780080970721000078?via%3Dihub) used for an MRI image of a dandelion used ~1W (2mm diameter coil)
- [Martinos Tabletop MRT](https://tabletop.martinos.org/index.php?title=Hardware:RF) TX line uses a 1.2W [ZHL-3A+](https://www.minicircuits.com/pdfs/ZHL-3A.pdf) power amplifier (gain 25dB, P1dB 32 dBm, 5dB noise), which they had to gate due to the carrier frequency coming through (~300€)
- [In this Halbach MRI Magnet Project that also uses MaRCoS](https://pure.tudelft.nl/ws/portalfiles/portal/150811992/NMR_in_Biomedicine_2023_Obungoloch_On_site_construction_of_a_point_of_care_low_field_MRI_system_in_Africa.pdf) a [ZX60-100VH+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZX60-100VH%2B) was used (they also used a passive TR switch based on crossed diodes and lambda/4 pi circuit)
- [The FOSS 2019 paper (Louis-Joseph and Lesot)](../../literature/related_projects/foss_nmr_spectrometer_15MHz.pdf) sends 37dBm max using a ZHL-5W-1 (gain: 46dB, max 40dBm, noise 4dB, mini-circuits) amp (~1500€)
- The [ARTIQ/Sinara Booster](https://github.com/sinara-hw/Booster/wiki) looks like a good inspiration
- The [ARTIQ/Sinara SiLPA](https://github.com/sinara-hw/SiLPA_HL/issues/1) seems relatively simple and seems to work down to 10MHz. Maybe ask them directly? Uses a CATV 75 ohm amplifier with 2 baluns for 50 ohm matching
  - Design a "simple" circuit myself based on a CATV amplifier as well?
- [JQI AOM Amp](https://github.com/JQIamo/aom-driver) seems ok, not as professional but meeting the specs and still quantum computation. Separate repo for [the GaN amplifier](https://github.com/JQIamo/GaN-Amplifier)
- The [OCRA Project uses a ZFL-500HLN+](https://www.minicircuits.com/pdfs/ZFL-500HLN.pdf) (gain: 20dB, noise: 3.8dB, P1DB: 17dBm) (~150€)
- MAGX-011086A power amplifier has an AN I could reproduce (4W) (~20€)

Next Steps:
1. Buy ZHL-3A+ power amplifier
2. Buy 1x PHA-13HLN+ evaluation board
3. Buy PHL-13HLN+ chips, try to use them with the same layout as the receive chips, test if power suffices
4. Do a bit more research here for a home-built one? or cheaper alternatives for a 1-5W amplifier

## TX/RX Switch
The T/R Switch needs to handle  ~5W, max 10W in transmit power (Bruker max. 5W!). Two main options exist:
- passive T/R Switch (lambda/4 + passive diodes) as built by Alex. Possibly change the Diodes to Schottky diodes for smaller leak-through power. Why aren't we using PIN diodes?
- active T/R switch (lambda/4 + pin diode)
  - built from discrete components (e.g. [this Github by Menküc](https://github.com/menkueclab/TR-Switch), explained in  [this Infineon AN](https://www.infineon.com/dgdl/Infineon-AN_1809_PL32_1810_172154_PIN%20diodes%20in%20RF%20sw%20applications-AN-v01_00-EN.pdf?fileId=5546d46265f064ff016643e2bc241042)) or the [OCRA T/R Switch](https://zeugmatographix.org/ocra/2021/09/30/transmit-receive-switch-for-the-ocra-tabletop-mri-system/) (PIN Diodes ~2CHF)
  - commercial chip (e.g. [M3SWA-2-50DR](https://www.minicircuits.com/pdfs/M3SWA-2-50DR.pdf) used by OpenCoreNMR for pulse modulation/[PE42520](https://www.psemi.com/pdf/datasheets/pe42520ds.pdf) (5W)/[QPC6324](https://www.mouser.ch/datasheet/2/412/QPC6324_Data_Sheet-1265756.pdf) (5W)/[MASW-000932](https://www.mouser.ch/datasheet/2/249/MASW_000932-838129.pdf) (max 80W) see [DigiKeys Antenna Switching Note](https://www.digikey.ch/en/articles/how-to-quickly-safely-switch-antenna-transducer-transmit-receive-modes) or [Digikeys RF Switch Note](https://www.digikey.de/de/articles/choosing-an-rf-switch)) ~5CHF-10CHF
  - [20CHF Commercial RF Switch](https://www.mikroe.com/rf-switch-click) used in [SiLPA](https://github.com/sinara-hw/SiLPA_HL/issues/1)
  
For simplicity of use, a passive switch would be advantageous if possible. The passive solution should leak only a little power that can be clamped by the protection diodes before the amplifier. This has the advantage that we can see the ringing of the coil and accurately start measuring after?

Next steps:
1. For now Alex' amplifier can be used the 6dBm output power that leaks from input to output can be clamped at every stage of the amplifier chain.
2. Since we don't have that much power the design could probably be made smaller, e.g. only one lambda/4 filter instead of three
3. Use Schottky Diodes instead of normal signal switching diodes for a lower power leak
4. A switch 


## Red Pitaya
The ADC of the RedPitaya is specified for an RF input voltage of 0.5Vpp. Its absolute maximum rating is 30VDC and 1Vpp RF (~4dBm). This has been verified by looking at the [used ADC](https://www.analog.com/media/en/technical-documentation/data-sheets/218543f.pdf) and the [RedPitaya Schematic](../../literature/instruments/Customer_Schematics_STEM122-16SDR_V1r1(Series1).PDF). Thus the input has to be protected from the power of the transmit cycle.

The easiest way to do this is to use a TVS diode for clamping the input to safe levels. Unfortunately, this severely degrades the ADCs performance according to [this Analog Devices Application Note](../../literature/instruments/rf-samp-adc-input-protection.pdf). The same AN suggests using [RB851Y](https://www.mouser.com/datasheet/2/348/rb851y-209815.pdf) Schottky diodes for ADC input protection

Next Steps:
1. Build 2x Protection diode blocks with 2x BYS-10 schottky diodes each for input protection (limit power to 4dBm/+-0.5V/1Vpp)

## Parts
A list of parts can be found in the [BOM](./bom.csv)

## Datasheets

Gain Block for Transmission:
- [ZFL-1000+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-1000%2B) - [Datasheet](./ZFL-1000.pdf)

Low Noise Amplifier for Reception:
- [ZFL-500LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-500LN%2B) - [Datasheet](./ZFL-500LN%2B.pdf)
- Alternative: [PHA-13LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=PHA-13LN%2B) - [Datasheet](./PHA-13LN%2B.pdf) - Still needs to be assembled and packaged according to [the instructions from the Martinos Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier)