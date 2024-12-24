import json
import time

import zmq

host = "0.0.0.0"
port = 30001

context = zmq.Context()
socket = context.socket(zmq.PUB)

socket.setsockopt(zmq.SNDBUF, 128 * 1024 * 1024)
socket.setsockopt(zmq.SNDHWM, 50000)

socket.bind(f"tcp://{host}:{port}")

# let the bind work
time.sleep(1)

body = bytearray(512 * 1024)

message = {
    "jsonversion": 5,
    "bitmode": 16,
    "fileIndex": 0,
    "detshape": [1, 4],
    "shape": [1024, 256],
    "size": 524288,
    "acqIndex": 2000,
    "frameIndex": 999,
    "progress": 100,
    "fname": "/dev/shm/gw/run",
    "data": 1,
    "completeImage": 1,
    "frameNumber": 2000,
    "expLength": 0,
    "packetNumber": 64,
    "detSpec1": 0,
    "timestamp": 0,
    "modId": 0,
    "row": 0,
    "column": 0,
    "detSpec2": 0,
    "detSpec3": 0,
    "detSpec4": 0,
    "detType": 3,
    "version": 2,
    "flipRows": 0,
    "quad": 0,
    "rx_roi": [0, 1023, 0, 255],
}

t0 = time.time()
for j in range(10000):
    message["frameNumber"] = j
    header = json.dumps(message)
    socket.send_multipart([header.encode(), body])
t1 = time.time()

header = json.dumps({"frameNumber": -1, "bitmode": 0})
socket.send_multipart([header.encode()])

time.sleep(1)

print(f"{t1 - t0:.2f}s")
