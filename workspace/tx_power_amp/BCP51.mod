***********************************************************
*
* BCP51
*
* Nexperia
*
* Medium power PNP Transistor
* IC   = 1 A
* VCEO = 45 V 
* hFE  = 63 - 250 @ 2V/150mA
* 
*
*
*
* Package pinning does not match Spice model pinning.
* Package: SOT 223
* 
* Package Pin 1: Base
* Package Pin 2: Collector
* Package Pin 3: Emitter
* Package Pin 4: Collector
* 
* Extraction date (week/year): 25/2019 
* Spicemodel includes temperature dependency
*
**********************************************************
*#
* Please note: Diode D1, Transistor Q2 and Resistor RQ 
* are dedicated to improve modeling of quasi
* saturation area and reverse mode operation
* and do not reflect physical devices.
*
.SUBCKT BCP51 1 2 3
Q1 1 2 3 MAIN 0.7456
Q2 11 2 3 MAIN 0.2544
RQ 1 11 9
D1 1 2 DIODE
*
.MODEL MAIN PNP
+ IS = 1.01E-13
+ NF = 1.006
+ ISE = 7.054E-15
+ NE = 1.3
+ BF = 157.5
+ IKF = 1
+ VAF = 15.62
+ NR = 1.006
+ ISC = 1.406E-14
+ NC = 1.325
+ BR = 13.46
+ IKR = 0.86
+ VAR = 80
+ RB = 10
+ IRB = 0.001
+ RBM = 2.5
+ RE = 0.1363
+ RC = 0.006969
+ XTB = 1.779
+ EG = 1.11
+ XTI = 5.698
+ CJE = 1.049E-10
+ VJE = 0.7623
+ MJE = 0.3879
+ TF = 1.115E-09
+ XTF = 2.02
+ VTF = 3.118
+ ITF = 0.759
+ PTF = 0
+ CJC = 4.998E-11
+ VJC = 0.9968
+ MJC = 0.4942
+ XCJC = 1
+ TR = 6.5E-08
+ CJS = 0
+ VJS = 0.75
+ MJS = 0.333
+ FC = 0.8944
.MODEL DIODE D
+ IS = 1.162E-15
+ N = 0.9998
+ BV = 1000
+ IBV = 0.001
+ RS = 8226
+ CJO = 0
+ VJ = 1
+ M = 0.5
+ FC = 0
+ TT = 0
+ EG = 1.11
+ XTI = 3
.ENDS
*