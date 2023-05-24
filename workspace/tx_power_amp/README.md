# TX Power Amplifier
Transmit power is expected to be in the area of Watts (Louis-Joseph and Leot (2022)). The maximum TX power of the Bruker Fourier 80 Benchtop spectrometer is 5W (37dBm) (through E-mail correspondence) and the [OpenCore NMR uses 1W TX power](https://www.sciencedirect.com/science/article/pii/B9780080970721000078?via%3Dihub) with a 2mm diameter tube as well. The maximum output power of the RedPitaya is -2dBm or 0.5Vpp thus a gain of 32dB to 39dB (to reach 1W or 5W respectively) would be required. A single amplifier with this gain and power output is not readily and cheaply available. Therefore a multi-stage approach is preferable.

## Previous Work/Inspiration
- The 2SK3475 and 2SK3476 RF transistors (MOSFET, N Channel) as used in this [The Stone Zone blog post](http://thestone.zone/radio/2021/06/05/power-amplifier.html) seem to be a good option for a few Watt amplifier
- [JQI AOM Amp](https://github.com/JQIamo/aom-driver) used a ZHL-2-8+ (535€) or a ZHL-3A-4+ (~239€) or a ZHL-5W-1+. [There's a paper as well](https://github.com/JQIamo/aom-driver/blob/master/aom_driver.pdf). Here they use a [HMC1099](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc1099.pdf) (gain 18.5 dB, P4dB 40dBm, noise 8dB, 120€) power amp. Datasheet includes typical application and evaluation PCB. Separate repo for [the GaN amplifier](https://github.com/JQIamo/GaN-Amplifier) they used alternatively. Preamp is a [HMC8410](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc8410.pdf) (gain 19dB, P1dB 21 dBm, noise 1.1dB).
- The IRF510 is (ab-)used by a lot of HAM radio enthusiasts for TX amplifiers in the 10m - 20m bands (30MHz - 15MHz).
  - [The Stone Zone Blog post about using an IRF510 Mosfet with a 2n2222 push-pull preamp](http://thestone.zone/radio/2020/12/13/multi-watt-amplifier.html) for a few Watt amplifier (up to 12W?).
  - [Here's a KiCAD board on GitHub with the IRF510](https://github.com/paulh002/IRF510-rf-amplifier).
  - [Another KiCAD project here](https://github.com/thaaraak/IRF510-Amplifier-v2) with a [circuit walkthrough on YouTube](https://www.youtube.com/watch?v=D4UhOmum_oU) as well.
  - [HAM Radio Amplifier based on IRF510](https://github.com/kholia/HF-PA-v6), [another project based on the same transistor](https://github.com/paulh002/IRF510-rf-amplifier)
- The 2SCR573 Power transistor (BJT, NPN) seems like a good alternative to the IRF510 used above as used in these preliminary tests in [The Stone Zone blog](http://thestone.zone/radio/2022/12/20/2sc573-testing.html)
- The PHA-202+ (30MHZ-2.7GHz, gain 18dB, P1dB 28 dBm, noise 3dB, 14€) was used in a [design in the ETH Quantum Optics Group](https://www.changpuak.ch/electronics/PHA-202+Amplifier.php). It seems to work well down to 2MHz despite the datasheet characterization starting at 30MHz. The design is very simple since the chip doesn't need any complex surrounding circuitry. Unfortunately, it doesn't quite reach the desired output levels of 30-37dBm. The design includes specifics for the heatsink, case and PCB. I originally found the chip in the [ARTIQ/Sinara SiLPA discussion](https://github.com/sinara-hw/SiLPA_HL/issues/1), where it was well-evaluated for its capabilities and ease of use, but there were concerns about temperature stability and lack of power. In the end, they went with the [QPB8808](https://www.qorvo.com/products/p/QPB8808) CATV (Cable Television) amplifier. Since CATV works on 75 Ohm impedance it needs a 1.5:1 balun at the input and output. A stripped-down version could be a valid option although the specified frequencies are too high - it might still work.
- [Martinos Tabletop MRI](https://tabletop.martinos.org/index.php?title=Hardware:RF) TX line uses a 1.2W [ZHL-3A+](https://www.minicircuits.com/pdfs/ZHL-3A.pdf) power amplifier (gain 25dB, P1dB 32 dBm, 5dB noise, ~300€), which they had to gate due to the carrier frequency coming through
- [In this Halbach MRI Magnet Project that also uses MaRCoS](https://pure.tudelft.nl/ws/portalfiles/portal/150811992/NMR_in_Biomedicine_2023_Obungoloch_On_site_construction_of_a_point_of_care_low_field_MRI_system_in_Africa.pdf) a [ZX60-100VH+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZX60-100VH%2B) (0.3-100MHz, max power: 1W/30dBm, gain 36dB, P1dB 30dBm, noise 4dB, ~350€) was used (they also used a passive TR switch based on crossed diodes and lambda/4 pi circuit)
- [The FOSS 2019 paper (Louis-Joseph and Lesot)](../../literature/related_projects/foss_nmr_spectrometer_15MHz.pdf) sends 37dBm max using a ZHL-5W-1 (gain: 46dB, max 40dBm, noise 4dB, ~1500€)
- The [OCRA Project uses a ZFL-500HLN+](https://www.minicircuits.com/pdfs/ZFL-500HLN.pdf) (gain: 20dB, noise: 3.8dB, P1DB: 17dBm, ~150€)
- The [MAGX-011086A](https://cdn.macom.com/datasheets/MAGX-011086A.pdf) GaN power amplifier has an AN I could reproduce (4W) (~20€)

## Background
- [Interesting general article about RF Power amps in NMR](http://www.cpcamps.com/introduction-to-nmr-mri-amplifiers.html)
- [IEEE Paper on how to build an RF power amp for NMR (10-25MHz)](https://ieeexplore.ieee.org/document/5163353)
- [OpenCore NMR](https://reader.elsevier.com/reader/sd/pii/S1090780708000670?token=C091614A806EFA2BEE0FBD33618073B2E48461C188AAA27B69640A102C862D004694C98189A10EBBDE6AD556E4D1E2EC&originRegion=eu-west-1&originCreation=20230510092722) uses a low pass filter  after the DAC to get rid of unwanted image frequencies due to the digital stepping through the waveform
- The [ARTIQ/Sinara Booster](https://github.com/sinara-hw/Booster/wiki) looks like a good inspiration
- The [ARTIQ/Sinara SiLPA](https://github.com/sinara-hw/SiLPA_HL/issues/1) as well

## Conclusions
1. Buy ZHL-3A+ power amplifier
2. Buy 1x PHA-13HLN+ evaluation board
3. Buy PHL-13HLN+ chips, try to use them with the same layout as the receive chips, test if power suffices
4. Do a bit more research here for a home-built one? or cheaper alternatives for a 1-5W amplifier