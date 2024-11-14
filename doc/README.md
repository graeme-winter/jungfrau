# Jungfrau

Repository for issue tracking and planning work for the development of the MORGUL data acquisition system for the JUNGFRAU 9M detector.

## Detector Control

Assumed to be similar / identical to operating the 1M. TODO document the steps needed to get the 2kHz frame rate working over and above the instructions in the getting started guide.

## Data Capture

The data capture with this detector is thesingle biggest challenge. Initial plan to use one SLS receiver process [per half module](./FORMAT.md) thus requiring 36 processes in total each consuming around 10Gb/s. Related tasks:

1. [build receiver](https://github.com/graeme-winter/jungfrau/issues/23)
2. [build test system](https://github.com/graeme-winter/jungfrau/issues/5)
3. confirm that we can consume 36 x 10Gb/s streams on one grace hopper system

## Pedestal Calculation

Want to be able to perform real-time recalculation of the pedestal values. On a GPU this will require [algorithms to estimate the median](https://github.com/graeme-winter/jungfrau/issues/22). This will also need to work with [both pedestal modes](https://github.com/graeme-winter/jungfrau/issues/17) though the medians are likely to be fairly similar. This will also need to recompute a pixel reliability mask on-the-fly though to some extent that will also need flood field data so define more than one calibration mode for acquisition.

## Data Correction

With the data in memory in the grace hopper system we will need to move the data into the GPU, apply corrections, move data out, mask and double pixels.

## Inline Analysis / Data Veto

This is possibly a stretch goal for the one system: being able to analyse the data as they are corrected to count the spots on every half-module (assuming masking of big pixels) or full module if not, to tag whether across that frame there is meaningful data. N.B. this will need to aggregate the results across the entire detector before making the go / no go call on saving the frame.
