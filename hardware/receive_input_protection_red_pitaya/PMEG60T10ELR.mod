*
*******************************************
*
*PMEG60T10ELR
*
*NEXPERIA Germany GmbH
*
*60V, 1A low leakage current Trench MEGA Schottky barrier rectifier
*
*
*VRmax     = 60V
*
*IFmax(AV) = 1A 
*VF        = 525mV  @ IF = 1A
*IR        = 0.12µA @ VR = 60V
*
*
*
*
*
*
*
*
*
*Package pinning does not match Spice model pinning.
*Package: CFP3 (SOD123W)
*
*Package Pin 1: Cathode 
*Package Pin 2: Anode 
* 
*
*
*Extraction date (week/year): 08/2018
*Simulator: SPICE3
*
*******************************************
*#
.SUBCKT PMEG60T10ELR 1 2
R1 1 2 8E+008
D1 1 2
+ DIODE1
D2 1 2
+ DIODE2
*
*The resistor R1 and the diode D2 do not reflect 
*physical devices but improve 
*only modeling in the reverse 
*mode of operation.
*
.MODEL DIODE1 D
+ IS = 3.5E-008
+ N = 1.09
+ BV = 70
+ IBV = 0.03
+ RS = 0.04
+ CJO = 3.25E-010
+ VJ = 2.6
+ M = 0.9
+ FC = 0.5
+ TT = 0
+ EG = 0.69
+ XTI = 2
.MODEL DIODE2 D
+ IS = 5E-012
+ N = 1
+ RS = 1.2
.ENDS
*





