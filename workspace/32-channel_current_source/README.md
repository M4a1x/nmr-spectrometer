# 32-Channel Current Source

To drive the magnet shims, a 32-channel current source is needed. More details can be found in the [SABR magnet and shim specifications](../SABR_Permanent_Magnet_and_Shim/General%20specifications%20of%20the%20NuevoMR%20shim%20driver%20current%20source.docx)

## Specification
- Price: 320CHF? (10CHF per channel)
- Current: +-500mA
- Voltage: +-2.5V
- Channels: 32
- Programmable
- Isolated

## Noise
The B field is propoertional to the current inside the windings


### Build myself
The premade devices I found are not suitable for low noise, high precision applications as they are often intended for LED dimming through PWM or for lower currents. The self designed supplies on the other hand are too expensive and offer a significantly higher current capability.

The goal of this design is to design a simple, easy-to-understand and modify, circuit from readily available parts with a low per-channel price and acceptable performance. It should be easy to build as well, ideally through hand soldering (i.e. no BGA/QFN chips)

Since I'm doing a basic linear regulation, the maximum voltage drop across the coil will be U = R * I = 1 Ohm * 500mA = 0.5V. The remaining power needs to be dissipated inside the supply. A power dissipation of ~1W-1.2W is acceptable in a mosfet/opamp without much consideration for heat management (see Infineon AN-2021-02, D2PAK, 0.5A, max. dT = 74K). Thus the maximum voltage drop over the regulator is U = P / I = 1W / 500mA = 2V. Therefore the power supply should be around 2.5V, maximum 2.9V, if everything is dissipated in a single device. Generally, the supply voltage should be chosen as low as possible.

- Red Pitaya SPI -> 32 DACs
- Simple OpAmp current source circuit (Tietze & Schenk)
- I found the [Howland current pump](https://www.ti.com/lit/an/snoa474a/snoa474a.pdf). This seems to be an option, but also poses high requirements on the resistor selection, is relatively complex to analyze and slow.
- [Martinos Lab](https://rflab.martinos.org/index.php?title=Current_driver:Current_driver) uses two opamps (OPA549, ~30chf) per channel in a push-pull configuration. There are several papers with an almost identical setup. e.g. [Bidirectional, Analog Current Source Benchmarked with Gray Molasses-Assisted Stray Magnetic Field Compensation](https://www.mdpi.com/2076-3417/11/21/10474?type=check_update&version=1)
- [A PI feedback control would also be an option](https://pubs.aip.org/aip/rsi/article/90/1/014701/368287/Ultra-low-noise-and-high-bandwidth-bipolar-current). This probably requires more tuning as the control loop is bigger, more parts and slower regulation.
- There's a comparison of the two MRI gradient boards on [MaRCoS wiki](https://github.com/vnegnev/marcos_extras/wiki/dacs)
- Get inspiration from the [OCRA1 Gradient board](https://zeugmatographix.org/ocra/2020/11/27/ocra1-spi-controlled-4-channel-18bit-dac-and-rf-attenutator/) (i.e.based on [this DAC (AD5781, 18bit 30€)](https://www.analog.com/media/en/technical-documentation/data-sheets/AD5781.pdf))
- Get inspiration from the Gradient Board [GPA-FHDO](https://github.com/menkueclab/GPA-FHDO) (uses the same architecture and parts as Martinos Lab above, i.e. OPAMP OPA549 (25chf) in push-pull config, input noise density 70nV/sqrt(Hz), current noise density 1pA/sqrt(Hz))
- Modular Design Example: [32 channel rf signal amplifier](https://www.opensourceimaging.org/project/32-channel-rf-receive-chain-amplifiers/)
- Probably need output filter (e.g. to prevent 60Hz noise)
- DAC:
  - For practicality reasons at least 4 channels per device are desirable so no MUX chip is needed for both I2C or SPI (daisy-chain). Prices steeply increase above 8 channels, with 8 channels usually being the cheapest per channel.
  - To get a resolution of 0.1mA at least 14bit are necessary. While 12-bit devices are significantly cheaper, the difference between 14 and 16-bit seems negligible. Thus a 16-bit device is chosen.
  - MCP4728 (4ch, 12bit, 2.25chf [0.562chf per channel], ridiculously cheap for some reason)
  - MCP48 (4ch, 12bit, 6.75chf [1.67chf per channel])
  - MCP47 (8ch, 12bit, 11chf [1.375chf per channel])
  - DAC80501 (1ch, 16bit, same as in Martinos/GPA-FHDO) ~6CHF on mouser.ch
  - DAC8555 (4ch, 16bit, 12.40CHF [3.1chf per channel], ext. ref, no daisy-chain)
  - DAC8568 (8ch, 16bit, int. ref, no daisy-chain)
  - DAC80508 (8ch, 16bit, ~21CHF [2.6chf per channel], QFN!)
  - **AD5676/AD5675 (R suffix with internal reference) (8ch, 16bit, ~20CHF [2.5chf per channel], TSSOP)**
- Voltage Reference:
  - See [TI's Voltage Reference Selection Guide (2015)](https://www.ti.com/lit/ml/snvd001a/snvd001a.pdf)
  - LM4041 1.225V fixed (100ppm/K drift, 0.1% initial acc., shunt, 0.5chf)
  - REF5025 (3ppm/K, 0.05% initial acc., series, 3CHF)
  - LM4140 (3ppm/K, 0.1% initial acc., series, 5CHF)
  - Higher Precision Reference REF01
- OpAmp
  - Power (I>=1A):
    - **NCS2372/NCV0372B/TCA0372 (dual, 1.35CHF)**
    - **L2720W/L272/L272D (dual, 2.70chf, identical to tca0372, better datasheet)**
    - OPA547 (1ch, 10chf)
    - OPA551(6chf, 200mA)
    - OPA2675 (dual, 3.37chf, QFN)
    - in Andrew/Conradi Paper: OPA025 (not found. maybe opa2544? 25chf), 0.5ohm current sense low side
  - Rail2Rail
    - **LMV358/LMV324 (Low Voltage)**
    - TLV904x (Ultra Low Voltage)
    - TLV9104 
- Audio Amp
  - LM1877 (dual, 1.5CHF)
- Supply: Linear regulator Dual LM317
  - Optional: Make precision by using TL431 reference (see eevblog)
  - REF01 for higher precision alternative
- Power Resistor: 1x WSC25155R000FEA (5 Ohm, 1W, 1%, 50ppm/K, 1CHF)

### Use LED current driver
- TL4242 (500mA, +-5%)
- HV9961 (+-3% current accuracy)
- NCR320PAS (250mA only)
- STCS05A (0.5A with a ±10% precision)
- TLD1211SJ (only up to 85mA)
- LM8040 (PWM controlled, accuracy?)
- LT3092 (200mA max)
- BCR420 (+-10%)


### Use current driver IC
- Device Power Supply IC (MAX32010, acc. 0.15%, 50€ pp)