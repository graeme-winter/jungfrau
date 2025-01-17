# ZeroMQ Correction Model

Basic idea is to capture zeroMQ packets and start to correct them in flight. At first, let's just pull in the JSON parsing and zeroMQ capture to enumerate the incoming packets with timestamps.

## Dependencies

Obviously this depends on zeroMQ and the `cppzmq` C++ bindings:

```
mamba install cppzmq zeromq
```

for the win. It also depends on a JSON library which is pulled in by `cmake`.
