# RX LNA Preamp

This folder contains the first amplifier in the RX chain, based on the [design of Martinos RF Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier) with the [PHA-13LN+](https://www.minicircuits.com/pdfs/PHA-13LN+.pdf) chip from mini-circuits.

This design could easily be adapted to be included in an all-in-one board including an RX preamplifier, RX amplifier, TX amplifier, TX power amplifier and TX/RX switch.

The design was adapted using the newest KiCAD version (7.0.2, 12.05.2023).

## Specifications
The receive amplifier needs to amplify the signal from uW level (~-30dbm, [Louis-Joesph and Lesot (2022)](../../literature/related_projects/foss_nmr_spectrometer_15MHz.pdf)) to around -2dbm (~0.5V @ 50Ohm) for the 16-bit ADC of the RedPitaya. Thus a gain of at least 28dB is needed. Previous work (see below) uses either a two or even three-stage design.

Furthermore, the design should be simple and easily reproducible. At best, it should be hand-solderable, without the need for a reflow oven or hot air gun. The parts should be easy to obtain and a low part count would be desirable as well. The target/carrier frequency is at 25MHz corresponding to the 1H Larmor frequency of the 0.6T magnet we're using.

One option would be to use an amplifier chain similar to [Martinos (MIT) lab](https://rflab.martinos.org/index.php?title=Main_Page) used in their MRI experiments for the reception. This consists of three stages, two PHA-13LN+ (~20€/eval board ~140€) and one ZFL-500LN+ (~125€). Sometimes the RX LNAs are already integrated into the T/R Switch - e.g. the [T/R Switch from Menküc](https://github.com/menkueclab/TR-Switch) uses the two PHA-13LN+ LNAs based on the design from Martinos lab. Since the maximum output level of the PHA-13LN+ is sufficiently high three PHA-LN13+ could be used as well.
> **TODO**
> Experimentally verify that 40dB (vs the 30dB estimate) are suitable for us, or if we need more/less amplification.

## Previous Work/Inspirations
- [Martinos Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier) uses a 3-stage design for their low-noise RF preamplifier. It consists of two PHA-13LN+ (Gain: 24dB, P1dB: 23dBm, Noise: 0.9dB @20MHz/5V) and one ZFL-500LN+ (Gain: 28dB, P1dB: 8dBm, Noise: 2.9dB, @5MHZ/15V) at the end before going into the measurement equipment. The two PHA-13LN+ are protected by BAV99 signal switching diodes (Vf=~0.7V), clamping the power at ~7dBm (PHA-13LN+ max. input pulse: 21dBm)
- The [tabletop MRI by Martinos Lab](https://tabletop.martinos.org/index.php?title=Hardware:RF) uses a 2-stage amplifier based on the [Gali-74+](https://www.minicircuits.com/pdfs/GALI-74+.pdf) (~4€/eval board 160€). (25dB gain, P1dB 19dbm, 2.7dB noise). Which is cheaper with comparable gain, but a higher noise figure. The RF-Switch uses [BYS-10](https://www.vishay.com/docs/86013/bys10.pdf) Schottky diodes with a V_f of 0.5V (-2dBm) for protection.
- [Hibino](https://www.sciencedirect.com/science/article/pii/S1090780718301745#b0110) used a CA-251F4 preamplifier (DC-10MHz, voltage 40dB gain, output power +-10mA max) which is unsuitable for our frequencies.
- The ZFL-500LN+ from mini-circuits has a gain of almost exactly 28dB when powered with at least 15V, with a P1dB of 8dBm over its whole specified range. Its noise figure is typically 2.9 dB.

## Filters
- The [T/R-Switch by Menküc](https://github.com/menkueclab/TR-Switch) uses a low-pass filter at the output of the LNA chain, in our case this could be e.g. [SCLF-30+](https://www.mouser.ch/datasheet/2/1030/SCLF_30_2b-1701154.pdf) (~19€), [SCLF-27+](https://www.mouser.ch/datasheet/2/1030/SCLF_27_2b-1701261.pdf) (~13€/eval board 120€), or a custom design bessel/butterworth/... Should be a lowpass, since all other possibly interesting atoms have a lower resonant frequency than a single 1H.

## TODOs
- [ ] Experimentally verify the PHA-13LN+ boards I made
- [ ] Experimentally verify if a filter is needed/useful
- [ ] Design my own filter (cheaper!)
- [ ] Based on the above results make a filter (breakout) board
- [ ] Integrate together with own T/R Switch and TX amplifiers on one board

## Conclusions
1. Buy 1x PHA-13LN+ evaluation board
2. Buy 1x SCLF-27+ evaluation board
3. Build 3x PHA-13LN+ individual gain blocks based on Martinos Lab Design
4. Build 2x protection diode blocks with a BAV99 dual-diode each for the evaluation boards
5. Build 1x protection diode blocks with BYS-10 Schottky diodes for the RedPitaya inputs
