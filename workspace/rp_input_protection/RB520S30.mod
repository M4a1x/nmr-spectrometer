***********************************************************
*
* RB520S30
*
* Nexperia
*
* 200 mA low VF MEGA Schottky barrier rectifiers
* IFmax = 200mA (average)
* VRmax = 30V
* VFmax = 600mV   @ IF = 200mA
* IRmax = 1µA     @ VR = 10V
*
*
*
*
* Package pinning does not match Spice model pinning.
* Package: SOD523
*
* Package Pin 1: Cathode
* Package Pin 2: Anode
*
*
* Extraction date (week/year): #
* Simulator: SPICE3
*
***********************************************************
*
* The resistor R1 does not reflect 
* a physical device. Instead it
* improves modeling in the reverse 
* mode of operation.
*
.SUBCKT RB520S30 1 2
D1 1 2 RB520S30
R1 1 2 1.26E+8 
*
.MODEL RB520S30 D 
+ IS = 7.409E-8 
+ N = 1.01 
+ BV = 44 
+ IBV = 0.001 
+ RS = 0.6919 
+ CJO = 2.402E-11 
+ VJ = 0.3356 
+ M = 0.4335 
+ FC = 0.5 
+ EG = 0.69 
+ XTI = 2 
.ENDS
*