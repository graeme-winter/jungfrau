import json
import sys
import time

import zmq

host = "0.0.0.0"
port = int(sys.argv[1])

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVBUF, 128 * 1024 * 1024)
socket.setsockopt(zmq.RCVHWM, 50000)

socket.connect(f"tcp://{host}:{port}")

found = []

t0 = 0

while True:
    messages = socket.recv_multipart()
    if not t0:
        t0 = time.time()
    header = json.loads(messages[0])
    if header["bitmode"] == 0:
        break
    n = int(header["frameIndex"])
    found.append(n)

t1 = time.time()

assert len(found) == max(found) + 1

print(f"{t1 - t0:.2f}s")
