# ZeroMQ interface

There is a built-in zeroMQ interface in the SLS receiver which means we can 
connect to this to pull data out...

```python
{'jsonversion': 5, 'bitmode': 16, 'fileIndex': 0, 'detshape': [1, 4], 'shape': [1024, 256], 'size': 524288, 'acqIndex': 102000, 'frameIndex': 999, 'progress': 100, 'fname': '/dev/shm/gw/run', 'data': 1, 'completeImage': 1, 'frameNumber': 102000, 'expLength': 0, 'packetNumber': 64, 'detSpec1': 0, 'timestamp': 0, 'modId': 0, 'row': 0, 'column': 0, 'detSpec2': 0, 'detSpec3': 0, 'detSpec4': 0, 'detType': 3, 'version': 2, 'flipRows': 0, 'quad': 0, 'rx_roi': [0, 1023, 0, 255]}
```

Followed by 524288 bytes corresponding to the raw image.

