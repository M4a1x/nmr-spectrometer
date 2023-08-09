*BAS321
*
*NXP Semiconductors
*
*General purpose diode
*
*
*
*
* 
*
*
*
*
*
*
*VRRM = 250V
*IFRM = 625mA @ tp = 0,5ms
*trr  = 50ns
*
*Package: SOD323
*
*Package Pin 1: cathode  
*Package Pin 2: Anode
*
*
*
*
*Simulator: SPICE2
*
******************************************
*
.SUBCKT BAS321 1 2
*
* The resistor R1 does not reflect
* a physical device. Instead it
* improves modeling in the reverse
* mode of operation.
*
R1 1 2 1.622E+10 
D1 1 2 BAS321
*
.MODEL BAS321 D 
+ IS = 3.648E-9 
+ N = 1.909 
+ BV = 260 
+ IBV = 2E-7 
+ RS = 0.7535 
+ CJO = 6.99E-13 
+ VJ = 0.2028 
+ M = 0.1151 
+ FC = 0.5 
+ TT = 3.462E-8 
.ENDS
