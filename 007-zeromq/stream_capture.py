import json
import sys

import zmq

host = "0.0.0.0"
port = int(sys.argv[1])

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVHWM, 50000)
socket.connect(f"tcp://{host}:{port}")

while True:
    messages = socket.recv_multipart()
    header = json.loads(messages[0])
    if header["bitmode"] == 0:
        break
    n = header["frameNumber"]
    if not n % 100:
        print(n)
        print(header)
        print(len(messages[1]))
