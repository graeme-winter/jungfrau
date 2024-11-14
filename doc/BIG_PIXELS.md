# Big Pixels

[As described elsewhere](./FORMAT.md) the bump bond layout gives rise to a small number of pixels which are effectively larger in one or both directions. With EIGER detectors these are expanded to be two or four virtual pixels, ensuring that the wider geometry is correct at the cost of (i) a little extra correction work and memory bandwidth and (ii) a slight loss in strict statistical correctness, as the shared values exhibit a lower variance than the surrounding "true" pixels. With JUNGFRAU, using `jungfraujoch`, these pixels are currently simply masked rather than being considered as useful measurements. The decision on how to handle the larger pixels for the 9M detector needs to balance:

1. the benefit of including the extra pixels
2. the cost of (i) expanding the pixels and (ii) handling the extra bytes
3. the cost of altering analysis software to handle that some pixels are larger

Assessing 1. here will require simulating the impact of including or not the pixels around each ASIC: this can be assessed with data from an EIGER 9M and some additional masking.

## Example Data Set

For this, using an example data set acquired on i04-1 with an EIGER 2XE 9M detector, from Thaumatin which has a fairly large unit cell along one edge giving sufficient measurements that this can be realistically assessed. Thaumatin has a high symmetry, so ignoring this and processing the data with a triclinic lattice will give a useful worst-case estimate on the impact on completeness.

## Protocol

Process the data as captured, manually apply a mask using a [python script](../004-issue-19-pixel-masker/big_pixel_masker.py) around every ASIC (a four pixel internal boundary) then reproces the data, compare the completeness and multiplicity of the data. The internal masks are:

![Masked image](./masked_modules.png)

## Results

Processing all the data gives:

```
                                             Overall    Low     High
High resolution limit                           1.15    3.12    1.15
Low resolution limit                          151.03  152.35    1.17
Completeness                                   65.9    99.2     2.2
Multiplicity                                    3.1     3.6     1.0
I/sigma                                        21.6    73.3     1.2
Rmerge(I)                                     0.051   0.030   0.000
Rmerge(I+/-)                                  0.041   0.026   0.000
Rmeas(I)                                      0.060   0.036   0.000
Rmeas(I+/-)                                   0.058   0.036   0.000
Rpim(I)                                       0.033   0.019   0.000
Rpim(I+/-)                                    0.041   0.026   0.000
CC half                                       0.998   0.997   0.000
Anomalous completeness                         58.9    96.4        
Anomalous multiplicity                          1.6     1.8     1.0
Anomalous correlation                        -0.064  -0.076   0.000
Anomalous slope                               1.426
dF/F                                          0.065
dI/s(dI)                                      1.345
Total observations                          1433839  127356     769
Total unique                                 466139   35086     769
```

The completeness is far below 1 as the crystals diffract to the corners of the detector. Adding in a mask for the big pixels has a very modest impact, to:

```
                                             Overall    Low     High
High resolution limit                           1.15    3.12    1.15
Low resolution limit                          151.03  152.35    1.17
Completeness                                   65.6    99.2     2.2
Multiplicity                                    3.0     3.5     1.0
I/sigma                                        21.3    71.5     1.2
Rmerge(I)                                     0.050   0.030   0.000
Rmerge(I+/-)                                  0.041   0.026   0.000
Rmeas(I)                                      0.060   0.036   0.000
Rmeas(I+/-)                                   0.058   0.036   0.000
Rpim(I)                                       0.033   0.019   0.000
Rpim(I+/-)                                    0.041   0.026   0.000
CC half                                       0.998   0.997   0.000
Anomalous completeness                         55.9    92.5        
Anomalous multiplicity                          1.6     1.8     1.0
Anomalous correlation                        -0.046  -0.074   0.000
Anomalous slope                               1.435
dF/F                                          0.065
dI/s(dI)                                      1.355
Total observations                          1381755  122869     768
Total unique                                 463800   35086     768
```

About 0.3% of the unique measurements, 3-4% of the overall measurements were lost: of these the more important as this may impact the number of unique data for a small scan.

## Conclusion

Not including the big pixels in the final data set is unlikely to be catastrophic, however if we _can_ do it in the analysis chain it is probably worthwhile, as the increase in the useful number of reflections in the final data set is measurable if not substantial.
