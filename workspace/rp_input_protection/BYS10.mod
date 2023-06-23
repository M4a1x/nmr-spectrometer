**********************************
* Model created by               *
*   Uni.Dipl.-Ing. Arpad Buermen *
*   arpad.burmen@ieee.org        *
* Copyright:                     *
*   Thomatronik GmbH, Germany    *
*   info@thomatronik.de          *
**********************************
*   SPICE3
* Model for BYS10_45
.subckt BYS10 1 2
ddio 1 2 legd
dgr 1 2 grd
.model legd d is = 3.85415E-006 n = 1.40358 rs = 0.0557528
+ eg = 0.758858 xti = 2.99661
+ cjo = 3.49905E-010 vj = 0.250479 m = 0.467611 fc = 0.5
+ tt = 1.4427E-009 bv = 49.5 ibv = 10 af = 1 kf = 0
.model grd d is = 1E-015 n = 1.13376 rs = 0.0323937
+ eg = 1.7057 xti = 2.02655
.ends
