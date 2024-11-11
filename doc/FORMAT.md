# Format

The data format needs to be sufficient to represent data with a saturation value typically around 10,000 counts - so 16 bits should be more than adequate. The values must also allow for masking i.e. recording a value for a pixel which indicates that the pixel value is untrusted, with the reason encoded in an external mask (which is assumed to be constant for the data set).

Since negative values are possible (if rare) the only logical option is to select a value which is unlikely to occur naturally, so for 16 bits `0x8000` i.e. 32,768 (unsigned) is selected: this value indicates that the pixel should be ignored.

## Format on Disk

The primary data come in the form of 4 streams each consisting of 256x1024 pixel arrays. These include double sized pixels around the edge of every module which should be ignored, or doubled in one or two directions as needed if the data are considered to be useful.
