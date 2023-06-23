*
* TCA0372 operational amplifier 
*"macromodel" subcircuit
*
* connections:
*  1 -   non-inverting input
*  2 -   inverting input
*  3 -   positive power supply
*  4 -   negative power supply
*  5 -   output
* 
* Fixed according to
* https://www.mikrocontroller.net/topic/437626
* Post von Helmut
*
.SUBCKT TCA0372  1 2 3 4 5
*
  c1   11 12 2.469E-12
  c2    6  7 28.00E-12
  dc    5 53 dx
  de   54  5 dx
  dlp  90 91 dx
  dln  92 90 dx
  dp    4  3 dx
  egnd 99  0 poly(2) (3,0) (4,0) 0 .5 .5
  fb    7 99 poly(5) vb vc ve vlp vln 0 10.33E6
+  -10E6 10E6 10E6 -10E6
  ga    6  0 11 12 193.5E-6
  gcm   0  6 10 99 6.120E-9
  iee   3 10 dc 39.40E-6
  hlim 90  0 vlim 1K
  q1   11  2 13 qx
  q2   12  1 14 qx
  r2    6  9 100.0E3
  rc1   4 11 5.167E3
  rc2   4 12 5.167E3
  re1  13 10 3.828E3
  re2  14 10 3.828E3
  ree  10 99 5.076E6
  ro1   8  5 5e0
  ro2   7 99 50
  rp    3  4 4.310E3
  vb    9  0 dc 0
  vc    3 53 dc 1.40
  ve   54  4 dc 1.40
  vlim  7  8 dc 0
  vlp  91  0 dc 20e2
  vln   0 92 dc 20e2
.model dx D(Is=800.0E-18)
.model qx PNP(Is=800.0E-18 Bf=196)
.ends
