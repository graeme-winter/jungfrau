# ZeroMQ interface

There is a built-in zeroMQ interface in the SLS receiver which means we can 
connect to this to pull data out...

```python
{'acqIndex': 102000,
 'bitmode': 16,
 'column': 0,
 'completeImage': 1,
 'data': 1,
 'detSpec1': 0,
 'detSpec2': 0,
 'detSpec3': 0,
 'detSpec4': 0,
 'detType': 3,
 'detshape': [1, 4],
 'expLength': 0,
 'fileIndex': 0,
 'flipRows': 0,
 'fname': '/dev/shm/gw/run',
 'frameIndex': 999,
 'frameNumber': 102000,
 'jsonversion': 5,
 'modId': 0,
 'packetNumber': 64,
 'progress': 100,
 'quad': 0,
 'row': 0,
 'rx_roi': [0, 1023, 0, 255],
 'shape': [1024, 256],
 'size': 524288,
 'timestamp': 0,
 'version': 2}
 ```

Followed by 524288 bytes corresponding to the raw image. This is the same for every image in the stream (TODO work out if there are performance limits?) then there is a last packet in the stream with no second part to the message and NULL values.
