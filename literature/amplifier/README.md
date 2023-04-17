# Amplifier

We need two amplifiers for the NMR spectrometer: A gain stage for the transmit path and a low noise amplifier (LNA) for the receive path. Both are connected between the TX/RX switch and the Red Pitaya in their respective paths.

## Circuit Diagram
```text
+------------+                +--------------+
|            |     |\         | RX/TX Switch |
|            |     | \        |              |
|         TX |-----|  +-------|---x  \       |         \ | /
|            |     | /        |       \      |          \|/
|            |     |/         |        \     |           |
|            |  Gain Block    |         \    |           |
| Red Pitaya |                |          +---|-----------+
|            |                |              |
|            |       /|       |              |
|            |      / |       |              |
|         RX |-----+  |-------|---x          |
|            |      \ |       |              |
|            |       \|       |              |
|            |      LNA       |              |
+------------+                +--------------+
```

## Datasheets

Gain Block for Transmission:
- [ZFL-1000+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-1000%2B) - [Datasheet](./ZFL-1000.pdf)

Low Noise Amplifier for Reception:
- [ZFL-500LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZFL-500LN%2B) - [Datasheet](./ZFL-500LN%2B.pdf)
- Alternative: [PHA-13LN+](https://www.minicircuits.com/WebStore/dashboard.html?model=PHA-13LN%2B) - [Datasheet](./PHA-13LN%2B.pdf) - Still needs to be assembled and packaged according to [the instructions from the Martinos Lab](https://rflab.martinos.org/index.php?title=Low-noise_RF_Preamplifier)