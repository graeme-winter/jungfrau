# Pixel Simulation

The conversion from the ADC readout to pixels is performed in two stages: first the pedestal is subtracted from the readout (i.e. the no-illumination ADC readout) then the subtracted value converted to an estimate of the deposited charge, in keV, before converting to photons.

From [S. Redford et al 2018 JINST 13 C01027](https://iopscience.iop.org/article/10.1088/1748-0221/13/01/C01027/pdf) the values for the gains are approximately 40 for G0 mode, -1.5 for G1, -0.1 for G2, with pedestals around 3000, 15000, 15000 respectively. These can be used, along with the approximate photon limits of the gain modes (around 25, 700, reported in the same paper) to estimate the readout which could be expected for a given photon count. A toy model for this:

```python
import math

G0E = 40 * 12.4
G1E = -1.5 * 12.4
G2E = -0.1 * 12.4

P0 = 3000
P1 = 15000
P2 = 15000

for j in range(160):
    j = math.pow(10, 0.025 * j)
    j0, j1, j2 = j * G0E + P0, j * G1E + P1, j * G2E + P2
    if j < 25:
        print(j, j0)
    elif j < 700:
        print(j, j1)
    else:
        print(j, j2)
```

Gives useful output:

![ADC readout vs. counts(./ADC.png)

This can be used to help convert from "real" data from an Eiger to an estimate of the readout value, prefixed with the gain mode bits (0, 1, 3).
