# TX/RX Switch

The T/R Switch needs to handle  ~5W, max 10W in transmit power (Bruker max. 5W!). Two main options exist:
- passive T/R Switch (lambda/4 + passive diodes) as built by Alex. Possibly change the Diodes to Schottky diodes for smaller leak-through power. Why aren't we using PIN diodes?
- active T/R switch (lambda/4 + pin diode)
  - built from discrete components (e.g. [this Github by Menküc](https://github.com/menkueclab/TR-Switch), explained in  [this Infineon AN](https://www.infineon.com/dgdl/Infineon-AN_1809_PL32_1810_172154_PIN%20diodes%20in%20RF%20sw%20applications-AN-v01_00-EN.pdf?fileId=5546d46265f064ff016643e2bc241042)) or the [OCRA T/R Switch](https://zeugmatographix.org/ocra/2021/09/30/transmit-receive-switch-for-the-ocra-tabletop-mri-system/) (PIN Diodes ~2CHF)
  - commercial chip (e.g. [M3SWA-2-50DR](https://www.minicircuits.com/pdfs/M3SWA-2-50DR.pdf) used by OpenCoreNMR for pulse modulation/[PE42520](https://www.psemi.com/pdf/datasheets/pe42520ds.pdf) (5W)/[QPC6324](https://www.mouser.ch/datasheet/2/412/QPC6324_Data_Sheet-1265756.pdf) (5W)/[HMC544A](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc544ae.pdf) (5W) used in Sinara Booster/[MASW-000932](https://www.mouser.ch/datasheet/2/249/MASW_000932-838129.pdf) (max 80W) see [DigiKeys Antenna Switching Note](https://www.digikey.ch/en/articles/how-to-quickly-safely-switch-antenna-transducer-transmit-receive-modes) or [Digikeys RF Switch Note](https://www.digikey.de/de/articles/choosing-an-rf-switch)) ~5CHF-10CHF
  - [20CHF Commercial RF Switch](https://www.mikroe.com/rf-switch-click) used in [SiLPA](https://github.com/sinara-hw/SiLPA_HL/issues/1)
  
For simplicity of use, a passive switch would be advantageous if possible. The passive solution should leak only a little power that can be clamped by the protection diodes before the amplifier. This has the advantage that we can see the ringing of the coil and accurately start measuring after it ringed down?

Next steps:
1. For now Alex' amplifier can be used the 6dBm output power that leaks from input to output can be clamped at every stage of the amplifier chain.
2. Since we don't have that much power the design could probably be made smaller, e.g. only one lambda/4 filter instead of three
3. Use Schottky Diodes instead of normal signal switching diodes for a lower power leak
4. A switch 
