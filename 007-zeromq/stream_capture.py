import json
import sys
import time

import zmq

host = "0.0.0.0"
port = int(sys.argv[1])

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVHWM, 50000)
socket.connect(f"tcp://{host}:{port}")

frames = []

t0 = None

while True:
    messages = socket.recv_multipart()
    header = json.loads(messages[0])
    if header["bitmode"] == 0:
        break
    n = header["frameIndex"]

    if n == 0:
        t0 = time.time()

    if not n % 1000:
        print(n)
    frames.append(n)

t1 = time.time()

print(f"Read {n+1} frames in {t1 - t0:.2f}s")

assert len(frames) == len(set(frames))

