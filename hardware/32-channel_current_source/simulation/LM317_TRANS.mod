* PSpice Model Editor - Version 16.2.0
*$
* LM317
*****************************************************************************
* (C) Copyright 2014 Texas Instruments Incorporated. All rights reserved.
*****************************************************************************
** This model is designed as an aid for customers of Texas Instruments.
** TI and its licensors and suppliers make no warranties, either expressed
** or implied, with respect to this model, including the warranties of
** merchantability or fitness for a particular purpose. The model is
** provided solely on an "as is" basis. The entire risk as to its quality
** and performance is with the customer.
*****************************************************************************
*
** Released by: WEBENCH Design Center, Texas Instruments Inc.
* Part: LM317
* Date: 11DEC2014 
* Model Type: TRANSIENT
* Simulator: PSPICE
* Simulator Version: 16.2.0.p001
* EVM Order Number:
* EVM Users Guide:
* Datasheet:SLVS044V�SEPTEMBER 1997�REVISED FEBRUARY 2013
*
* Model Version: Final 1.00
*
*****************************************************************************
*
* Updates:
*
* Final 1.00
* Release to Web
*
*****************************************************************************
.SUBCKT LM317_TRANS IN ADJ OUT_0 OUT_1
R_R1         VXX IN  {RINP}  
R_R6         N242982 VYY  10 TC=0,0 
R_R5         VZZ VYY  {ROUT}  
E_ABM1         N242982 0 VALUE { MIN(V(VXX), (V(Vzz)+(ILIM*ROUT)))    }
R_R2         N222524 VXX  {PSRR*RINP}  
R_U1_R2         0 U1_N26728  1G  
E_U1_ABM5         U1_N31197 0 VALUE { MIN(V(U1_N26728),  
+ MAX(V(IN) - {DROP}, 0))   }
C_U1_C2         0 U1_N26728  1n  
R_U1_R1         0 U1_N08257  1G  
R_U1_R4         U1_N28933 U1_N26728  10 TC=0,0 
R_U1_R5         U1_N31197 N222524  10 TC=0,0 
C_U1_C3         0 N222524  1n  
X_U1_U2         IN U1_N12783 U1_N12664 U1_UVLO_OK COMPHYS_BASIC_GEN PARAMS:
+  VDD=1 VSS=0 VTHRESH=0.5
C_U1_C1         0 U1_N08257  {1e-6*SQRT(TTRN)}  
V_U1_V4         U1_N12783 0 {UVLO}
V_U1_V3         U1_N12664 0 {UHYS}
E_U1_ABM6         U1_EN_OUT 0 VALUE { IF(V(U1_UVLO_OK)> 0.6, {VREF}, 0)    }
R_U1_R3         U1_EN_OUT U1_N08257  {3.333e5*SQRT(TTRN)} TC=0,0 
E_U1_ABM4         U1_N28933 0 VALUE { V(U1_N08257)*
+  (ABS(V(OUT_0))/(ABS(V(OUT_0)-v(ADJ))))    }
X_U2         0 OUT_0 d_d PARAMS:
X_F1    VZZ OUT_0 IN VYY LM317_TRANS_F1 
C_C1         VXX IN  {1/(6.28*RINP*POLE)}  
C_C2         VXX N222524  {1/(6.28*PSRR*RINP*ZERO)}  
C_C3         0 VYY  1n  
.PARAM  psrr=7.9432e-4 uvlo=0 ilim=2.2 pole=15k rinp=1e7 zero=100e6 rout=0.4m
+  ttrn=1e-4 vref=1.25 uhys=0 drop=.5
.ENDS LM317_TRANS
*$
.SUBCKT LM317_TRANS_F1 1 2 3 4  
F_F1         3 4 VF_F1 1
VF_F1         1 2 0V
.ENDS LM317_TRANS_F1
*$
.SUBCKT COMP_BASIC_GEN INP INM Y PARAMS: VDD=1 VSS=0 VTHRESH=0.5	
E_ABM Yint 0 VALUE {IF (V(INP) > 
+ V(INM), {VDD},{VSS})}
R1 Yint Y 1
C1 Y 0 1n
.ENDS COMP_BASIC_GEN
*$
.SUBCKT COMPHYS_BASIC_GEN INP INM HYS OUT PARAMS: VDD=1 VSS=0 VTHRESH=0.5	
EIN INP1 INM1 INP INM 1 
EHYS INP1 INP2 VALUE { IF( V(1) > {VTHRESH},-V(HYS),0) }
EOUT OUT 0 VALUE { IF( V(INP2)>V(INM1), {VDD} ,{VSS}) }
R1 OUT 1 1
C1 1 0 5n
RINP1 INP1 0 1K
.ENDS COMPHYS_BASIC_GEN
*$
.SUBCKT COMPHYS2_BASIC_GEN INP INM HYS OUT PARAMS: VDD=1 VSS=0 VTHRESH=0.5	
+ T=10
EIN INP1 INM1 INP INM 1 
EHYS INM2 INM1 VALUE { IF( V(1) > {VTHRESH},-V(HYS)/2,V(HYS)/2) }
EOUT OUT 0 VALUE { IF( V(INP1)>V(INM2), {VDD} ,{VSS}) }
R1 OUT 1 1
C1 1 0 {T*1e-9}
RINP1 INP1 0 10K
RINM2 INM2 0 10K
.ENDS COMPHYS2_BASIC_GEN
*$
.SUBCKT D_D 1 2
D1 1 2 DD
.MODEL DD D (IS=1E-015 N=0.01 TT=1e-011)
.ENDS D_D
*$

