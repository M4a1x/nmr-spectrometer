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