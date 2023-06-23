# 32-Channel Current Source

To drive the magnet shims, a 32-channel current source is needed. More details can be found in the [SABR magnet and shim specifications](../SABR_Permanent_Magnet_and_Shim/General%20specifications%20of%20the%20NuevoMR%20shim%20driver%20current%20source.docx)

## Specification
- Price: 320CHF? (10CHF per channel)
- Current: +-500mA
- Voltage: +-2.5V
- Channels: 32
- Noise:
- Programmable
- Isolated

## Noise
The B field is propoertional 

## Ideas
- Supply: Linear regulator Dual LM317
  - Optional: Make precision by using TL431 reference (see eevblog)
  - REF01 for higher precision alternative
- Cheapest 16-bit DAC per channel available on digikey/mouser: AD5676/AD5675 (20CHF/2.5CHF per Channel)
  - Voltage Reference LM4041 1.225V fixed (for 5V DAC operation, 0.5chf)
  - Higher Precision Reference REF01
- Simple OpAmp current source circuit (Tietze & Schenk)
- OPAMP (slew rate, GBW, offset dnc):
  - NCS2372/NCV0372B/TCA0372 (dual, 1.35CHF)
  - L2720W/L272/L272D (dual, 2.70chf, identical to tca0372)
  - OPA547 (single, 10CHF)
  - OPA2675 (dual, 3.37chf)
- Audio Amp
  - LM1877 (dual, 1.5CHF)
- Power Resistor: 1x WSC25155R000FEA (5 Ohm, 1W, 1%, 50ppm/K, 1CHF)
### Build myself
- Red Pitaya SPI -> 32 DACs
- I found the [Howland current pump](https://www.ti.com/lit/an/snoa474a/snoa474a.pdf) which looks kind of like what the [Martinos Lab](https://rflab.martinos.org/index.php?title=Current_driver:Current_driver) is doing. Does this also work for our specs?
- I should probably simulate this in LT-Spice?
- There's a comparison of the two MRI gradient boards on [MaRCoS wiki](https://github.com/vnegnev/marcos_extras/wiki/dacs)
- Get inspiration from the [OCRA1 Gradient board](https://zeugmatographix.org/ocra/2020/11/27/ocra1-spi-controlled-4-channel-18bit-dac-and-rf-attenutator/) (i.e.based on [this DAC (AD5781, 18bit 30€)](https://www.analog.com/media/en/technical-documentation/data-sheets/AD5781.pdf))
- Get inspiration from the Gradient Board [GPA-FHDO](https://github.com/menkueclab/GPA-FHDO) (uses the same architecture and parts as Martinos Lab above, i.e. OPAMP OPA549 (25chf) in push-pull config, input noise density 70nV/sqrt(Hz), current noise density 1pA/sqrt(Hz))
- Probably need output filter (e.g. to prevent 60Hz noise)
- For DAC: DAC80501 (same as in Martinos/GPA-FHDO) ~6CHF on mouser.ch
- For OpAmp: OPA547(10chf), OPA551(6chf)
- in Andrew/Conradi Paper: OPA025 (not found. maybe opa2544? 25chf), 0.5ohm current sense low side
- Circuit: As simple as possible. See notebook 02.05.2023
- Modular Design Example: [32 channel rf signal amplifier](https://www.opensourceimaging.org/project/32-channel-rf-receive-chain-amplifiers/)

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