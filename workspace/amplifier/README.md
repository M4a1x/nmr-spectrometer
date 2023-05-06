# Amplifier

We need two amplifiers for the NMR spectrometer: A gain stage for the transmit path and a low noise amplifier (LNA) for the receive path. Both are connected between the TX/RX switch and the Red Pitaya in their respective paths.

## Circuit Diagram
```text
+------------+                +--------------+
|            |     |\         | RX/TX Switch |
|            |     | \        |              |
|         TX |-----|  +-------|---x  \       |         \ | /
|            |     | /        |       \      |          \|/
|            |     |/         |        \     |           |
|            |  Gain Block    |         \    |           |
| Red Pitaya |                |          +---|-----------+
|            |                |              |
|            |       /|       |              |
|            |      / |       |              |
|         RX |-----+  |-------|---x          |
|            |      \ |       |              |
|            |       \|       |              |
|            |      LNA       |              |
+------------+                +--------------+
```

## Specifications

Transmit Power is expected to be in the area of Watts to tens of Watts, while the reception power is expected to be in the area of uW [Louis-Joseph and Lesot (2019)](../related_projects/foss_nmr_spectrometer_15MHz.pdf). Thus a single amplifier is often not enough and a multi stage approach is preferable. One option would be to use an amplifier change similar to [Martinos (MIT) lab](https://rflab.martinos.org/index.php?title=Main_Page).

## LNA RX Amplifier
The receive Amplifier needs to amplify the signal from uW level (~-30dbm) to around -2dbm (~0.5V @ 50Ohm) for the 16-bit ADC of the RedPitaya. Thus a gain of 28dB is needed.

- The ZFL-500LN+ from mini-circuits has a gain of almost exactly 28dB when powered with at least 15V, with a P1dB of 8dBm over its whole specified range. Its noise figure is at typ. 2.9dB.
- A good alternative with lower noise, but also lower gain would be the PHA-13LN+ as used by [Martinos Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier). It has a gain of 24dB, a low noise figure of 0.9dB typ. and a P1dB of 24 dBm over its whole specified range. In Martinos lab this is used in a 3 stage amplifier of 2x PHA-13LN+ and 1x ZFL-500LN+. The amplifier is protected by a BAV99 signal switching diode (Vf=~1V) clamping the power at ~9-10dBm (amplifier max. 21dBm pulse).
- The [tabletop MRI by Martinos Lab](https://tabletop.martinos.org/index.php?title=Hardware:RF) uses a 2 stage amplifier based on the [Gali-74+](https://www.minicircuits.com/pdfs/GALI-74+.pdf). (25dB gain, P1dB 19dbm, 2.7dB noise). The RF-Switch uses [BYS-10](https://www.vishay.com/docs/86013/bys10.pdf) Schottky diodes with a Vf of 0.5V.

## TX Power Amplifier
- [Martinos Tabletop MRT](https://tabletop.martinos.org/index.php?title=Hardware:RF) TX line uses a 1.2W [ZHL-3A+](https://www.minicircuits.com/pdfs/ZHL-3A.pdf) power amplifier (gain 25dB, P1dB 32 dBm, 5dB noise), which they had to gate due to the carrier frequency coming through.

## Red Pitaya
The ADC of the RedPitaya is specified for an RF input voltage of 0.5Vpp. Its absolute maximum rating is 30VDC and 1Vpp RF (~4dBm). This has been verified by looking at the [used ADC](https://www.analog.com/media/en/technical-documentation/data-sheets/218543f.pdf) and the [RedPitaya Schematic](../../literature/instruments/Customer_Schematics_STEM122-16SDR_V1r1(Series1).PDF). Thus the input has to be protected from the power of the transmit cycle.

The easiest way to do this is to use a TVS diode for clamping the input to safe levels. Unfortunately, this severely degrades the ADCs performance according to [this Analog Devices Application Note](../../literature/instruments/rf-samp-adc-input-protection.pdf). The same AN suggests using [RB851Y](https://www.mouser.com/datasheet/2/348/rb851y-209815.pdf) Schottky diodes for ADC input protection

## Datasheets

Gain Block for Transmission:
- [ZFL-1000+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-1000%2B) - [Datasheet](./ZFL-1000.pdf)

Low Noise Amplifier for Reception:
- [ZFL-500LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-500LN%2B) - [Datasheet](./ZFL-500LN%2B.pdf)
- Alternative: [PHA-13LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=PHA-13LN%2B) - [Datasheet](./PHA-13LN%2B.pdf) - Still needs to be assembled and packaged according to [the instructions from the Martinos Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier)