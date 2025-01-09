import sys
import time

import numpy
import h5py
import hdf5plugin
import zmq

host = sys.argv[1]
port = int(sys.argv[2])

compression = {"compression": 32008, "compression_opts": (0, 2)}

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.setsockopt(zmq.RCVHWM, 50000)
socket.connect(f"tcp://{host}:{port}")

total = int(sys.argv[3])

fout = h5py.File(f"data_{port}.h5", "w")

data = fout.create_dataset(
    "data",
    shape=(total, 256, 1024),
    chunks=(1, 256, 1024),
    dtype=numpy.uint16,
    **compression,
)

timestamp = numpy.zeros(shape=(total,), dtype=numpy.float64)

for count in range(total):
    messages = socket.recv_multipart()
    frame = int.from_bytes(messages[0], byteorder="little")
    offset = (frame, 0, 0)
    data.id.write_direct_chunk(offset, messages[1])
    timestamp[frame] = time.time()

fout.create_dataset("timestamp", shape=(total,), data=timestamp, dtype=numpy.float64)

fout.close()
