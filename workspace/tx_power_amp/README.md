# TX Power Amplifier
Transmit power is expected to be in the area of Watts (Louis-Joseph and Leot (2022)). The maximum TX power of the Bruker Fourier 80 Benchtop spectrometer is 5W (37dBm) (through E-mail correspondence) and the [OpenCore NMR uses 1W TX power](https://www.sciencedirect.com/science/article/pii/B9780080970721000078?via%3Dihub) with a 2mm diameter tube as well. The maximum output power of the RedPitaya is -2dBm or 0.5Vpp thus a gain of 32dB to 39dB (to reach 1W or 5W respectively) would be required. A single amplifier with this gain and power output is not readily and cheaply available. Therefore a multi-stage approach is preferable.

## Previous Work/Inspiration
- The [NPTB00004A](https://www.mouser.ch/datasheet/2/249/NPTB00004A-1109174.pdf) (5W/37dBm, gain 23dB @900MHz, 70% efficiency, DC-6GHz, 20€) found on mouser, used in [ARTIQ/Sinara Booster (see below)](https://github.com/sinara-hw/Booster/releases) as well which uses an [ADL5535](https://www.mouser.ch/datasheet/2/609/ADL5535-3120463.pdf)/[ADL5536](https://www.mouser.ch/datasheet/2/609/ADL5536-3120503.pdf) (20MHz-1GHz, gain 16dB/20dB, 5€) then a [PHA-1+](https://www.minicircuits.com/pdfs/PHA-1+.pdf) (50MHz-6GHz, gain 17dB, P1dB 22dBm, 3€) as preamps
- The [2SK3475](https://www.mouser.ch/datasheet/2/408/2SK3475_datasheet_en_20070219-3106972.pdf) (P0 630mW, 2€) and [2SK3476](https://www.mouser.ch/datasheet/2/408/2SK3476_datasheet_en_20140301-3106903.pdf) (P0 7W, 5€) RF transistors (MOSFET, N Channel) as used in this [The Stone Zone blog post](http://thestone.zone/radio/2021/06/05/power-amplifier.html) seem to be a good option for a few Watt amplifier
- The IRF510 is (ab-)used by a lot of HAM radio enthusiasts for TX amplifiers in the 10m - 20m bands (30MHz - 15MHz).
  - [The Stone Zone Blog post about using an IRF510 Mosfet with a 2n2222 push-pull preamp](http://thestone.zone/radio/2020/12/13/multi-watt-amplifier.html) for a few Watt amplifier (up to 12W?).
  - [Here's a KiCAD board on GitHub with the IRF510](https://github.com/paulh002/IRF510-rf-amplifier).
  - [Another KiCAD project here](https://github.com/thaaraak/IRF510-Amplifier-v2) with a [circuit walkthrough on YouTube](https://www.youtube.com/watch?v=D4UhOmum_oU) as well.
  - [HAM Radio Amplifier based on IRF510](https://github.com/kholia/HF-PA-v6), [another project based on the same transistor](https://github.com/paulh002/IRF510-rf-amplifier)
- [JQI AOM Amp](https://github.com/JQIamo/aom-driver) used a ZHL-2-8+ (535€) or a ZHL-3A-4+ (~239€) or a [ZHL-5W-1+](https://www.minicircuits.com/pdfs/ZHL-5W-1+.pdf) (~1500€). [There's a paper as well](https://github.com/JQIamo/aom-driver/blob/master/aom_driver.pdf). Here they use a [HMC1099](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc1099.pdf) (gain 18.5 dB, P4dB 40dBm, noise 8dB, 120€) power amp. Datasheet includes typical application and evaluation PCB. Separate repo for [the GaN amplifier](https://github.com/JQIamo/GaN-Amplifier) they used alternatively. Preamp is a [HMC8410](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc8410.pdf) (gain 19dB, P1dB 21 dBm, noise 1.1dB, ~50€).
- The [2SCR573](https://fscdn.rohm.com/en/products/databook/datasheet/discrete/transistor/bipolar/2scr573d3tl-e.pdf) Power transistor (BJT, NPN) seems like a good alternative to the IRF510 used above as used in these preliminary tests in [The Stone Zone blog](http://thestone.zone/radio/2022/12/20/2sc573-testing.html)
- The [PHA-202+](https://www.minicircuits.com/pdfs/PHA-202+.pdf) (30MHZ-2.7GHz, gain 18dB, P1dB 28 dBm, noise 3dB, 14€) was used in a [design in the ETH Quantum Optics Group](https://www.changpuak.ch/electronics/PHA-202+Amplifier.php). It seems to work well down to 2MHz despite the datasheet characterization starting at 30MHz. The design is very simple since the chip doesn't need any complex surrounding circuitry. Unfortunately, it doesn't quite reach the desired output levels of 30-37dBm. The design includes specifics for the heatsink, case and PCB. I originally found the chip in the [ARTIQ/Sinara SiLPA discussion](https://github.com/sinara-hw/SiLPA_HL/issues/1), where it was well-evaluated for its capabilities and ease of use, but there were concerns about temperature stability and lack of power. In the end, they went with the [QPB8808](https://www.qorvo.com/products/p/QPB8808) (50MHz-1.2GHz, gain 20dB, P1dB +33dBm, noise 4.5dB, ~29€) CATV (Cable Television) amplifier. Since CATV works on 75 Ohm impedance it needs a 1.5:1 balun at the input and output. A stripped-down version could be a valid option although the specified frequencies are too high - it might still work. Uses an ADL5536 and a PHA-1+ as preamps (same as Sinara Booster above)
- [Martinos Tabletop MRI](https://tabletop.martinos.org/index.php?title=Hardware:RF) TX line uses a 1.2W [ZHL-3A+](https://www.minicircuits.com/pdfs/ZHL-3A.pdf) power amplifier (gain 25dB, P1dB 32 dBm, 5dB noise, ~300€), which they had to gate due to the carrier frequency coming through
- [In this Halbach MRI Magnet Project that also uses MaRCoS](https://pure.tudelft.nl/ws/portalfiles/portal/150811992/NMR_in_Biomedicine_2023_Obungoloch_On_site_construction_of_a_point_of_care_low_field_MRI_system_in_Africa.pdf) a [ZX60-100VH+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZX60-100VH%2B) (0.3-100MHz, max power: 1W/30dBm, gain 36dB, P1dB 30dBm, noise 4dB, ~350€) was used (they also used a passive TR switch based on crossed diodes and lambda/4 pi circuit)
- [The FOSS 2019 paper (Louis-Joseph and Lesot)](../../literature/related_projects/foss_nmr_spectrometer_15MHz.pdf) sends 37dBm max using a ZHL-5W-1 (gain: 46dB, max 40dBm, noise 4dB, ~1500€)
- The [OCRA Project uses a ZFL-500HLN+](https://www.minicircuits.com/pdfs/ZFL-500HLN.pdf) (gain: 20dB, noise: 3.8dB, P1DB: 17dBm, ~150€)
- The [MAGX-011086A](https://cdn.macom.com/datasheets/MAGX-011086A.pdf) GaN power amplifier (gain 24.6dB @ 900MHz, 37dBm max, has a typical application circuit I could reproduce (4W) (~20€)
- The [PHA-13HLN+](https://www.minicircuits.com/pdfs/PHA-13HLN+.pdf) (gain 24dB, P1dB 27.3dBm, noise 1.1dB) has a maximum power of 28.7dBm typically (~0.5W)

## Background
- [Interesting general article about RF Power amps in NMR](http://www.cpcamps.com/introduction-to-nmr-mri-amplifiers.html)
- [IEEE Paper on how to build an RF power amp for NMR (10-25MHz)](https://ieeexplore.ieee.org/document/5163353)
- [OpenCore NMR](https://reader.elsevier.com/reader/sd/pii/S1090780708000670?token=C091614A806EFA2BEE0FBD33618073B2E48461C188AAA27B69640A102C862D004694C98189A10EBBDE6AD556E4D1E2EC&originRegion=eu-west-1&originCreation=20230510092722) uses a low pass filter  after the DAC to get rid of unwanted image frequencies due to the digital stepping through the waveform
- The [ARTIQ/Sinara Booster](https://github.com/sinara-hw/Booster/wiki) looks like a good inspiration
- The [ARTIQ/Sinara SiLPA](https://github.com/sinara-hw/SiLPA_HL/issues/1) as well

## Discussion
The cheapest option with the highest power output which is still relatively easy to build based on the above findings would be a design based on the RF transistors 2SK3475 (16dB, 2€) and 2SK3476 (11dB, 5€). To get to 39dB amplification needed, another 12dB would be needed. Again the ADL5535 (16dB) could be used for that? probably in conjunction with a 3dB pi attenuator (see e.g. Booster schematic)

The next option would be using the PHA-202+ amplifier (18dB, 14€) with a preamplifier, e.g. the ADL5535 (16dB, 5€) from Booster. This would be slightly simpler as we'd be using a finished amp and preamp, but would have less max. power (~1W).

The last option would be using the NPTB00004A transistor (23dB) together with the ADL5535 (16dB) to reach 39dB, basically a stripped-down Booster.

There are a lot of options for preamplifiers though, e.g. a QPA4586A, QPA7489 would probably work as well even (but their specified range is rather large compared to the ADL5535/6). They are roughly the same price (~4€).

The two RF transistors of the first option are not recommended for new designs and the PHA-202+ option only reaches 1W output power. The last option also consists of a power transistor requiring my own bias, supply and matching calculations. Thus the simplest first step would be to build the PHA-202+ with a preamp. In a further step, the PHA-202+ could be replaced either with the QPB8808 as in SiLAS which wouldn't require any special calculations, but matching of 75 to 50 Ohm or a self-designed amplifier based on a transistor.

[Building my own amplifier](https://w3axl.com/?p=308) based on the transistors with correct power supply, biasing and input/output matching networks [or matched feedback networks](http://www.w1ghz.org/small_proj/Simple_Broadband_Power_Amplifiers.pdf) would probably need more time and research.

## Conclusion
1. Buy ZHL-3A+ power amplifier
2. Buy a SCLF-27+ filter for output filtering
3. Design board based on PHA-202+ and ADL5535 for 1W PA
4. Design own power amplification stage using an RF transistor, e.g. NPTB00004A

