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

t0 = -1

while True:
    messages = socket.recv_multipart()
    if t0 < 0:
        t0 = time.time()
    header = json.loads(messages[0])
    if header["bitmode"] == 0:
        break
    n = header["frameIndex"] + 1
    if not n % 1000:
        print(n, time.time() - t0)
