# Jungfrau Simulator

The [SLS detector software](https://slsdetectorgroup.github.io/devdoc/) includes simulators which can be used to simulate the behaviour of the detectors. These are available if you compile the code with `SLS_USE_SIMULATOR=ON` i.e.

```
git clone git@github.com:slsdetectorgroup/slsDetectorPackage.git
mkdir slsDetectorPackage-build
cd slsDetectorPackage-build
cmake -DCMAKE_INSTALL_PREFIX=${HOME}/sls -DSLS_USE_SIMULATOR=ON ../slsDetectorPackage
make
```

The configuration should be very similar to the real detector: this includes pointers to the detector configuration, the frame receiver and the configuration of each end.

## Jungfrau Configuration

The running 1M configuration at the end of the last experiments was:

```
hostname i24-jf1md-00+i24-jf1md-01+

0:rx_tcpport 1954
1:rx_tcpport 1955

rx_hostname bl24i-sc-jcu01+bl24i-sc-jcu01+

0:udp_srcip 192.168.200.201
0:udp_dstip 192.168.200.200
0:udp_dstport 32410

0:udp_srcip2 192.168.200.202
0:udp_dstip2 192.168.200.200
0:udp_dstport2 32411

1:udp_srcip 192.168.200.203
1:udp_dstip 192.168.200.200
1:udp_dstport 42410

1:udp_srcip2 192.168.200.204
1:udp_dstip2 192.168.200.200
1:udp_dstport2 42411

numinterfaces 2

fwrite 0

rx_zmqfreq 1
rx_zmqhwm 50000
rx_zmqstream 1

temp_control 1
temp_threshold 55

exptime 0.01
frames 1
speed full_speed
```

This sets up the hostname to talk to over the 1Gb/s copper lines to control the detector, the machine where the frame receiver is running and the UDP configuration to talk over the fast links between the two. The simulation configuration should be similar to this, though the examples all use `localhost` for the hostname for simplicity.

## Simulator Configuration

Start with a trivial configuration, which has a single module (though with two channels configured) and everything hooked into loopback addresses on `127.0.0.1`:

```
hostname localhost+

0:rx_tcpport 1954

rx_hostname localhost+

0:udp_srcip 127.0.0.1
0:udp_dstip 127.0.0.1
0:udp_dstport 30001

0:udp_srcip2 127.0.0.1
0:udp_dstip2 127.0.0.1
0:udp_dstport2 30002

numinterfaces 2

fwrite 0

rx_zmqfreq 1
rx_zmqhwm 50000
rx_zmqstream 1

temp_control 1
temp_threshold 55

exptime 0.001
frames 1000
speed full_speed

fformat binary
fwrite 1
fpath /dev/shm/gw

powerchip 1
```

To use this you then need to start the jungfrau simulator:

```
./jungfrauDetectorServer_virtual
```

which will then listen to everything, start the frame receiver:

```
./slsReceiver
```

though maybe the "multi receiver" is what will be needed here, then finally use the sls control programs to send the configuration above, and start the acquisition:

```
./sls_detector_put config virtual_jf.config 
./sls_detector_acquire
```

N.B. this sets up a shared memory area which handles much of the state.

## Test with the Grace Hopper

Connected up the Connext-X 7, hard coded the IP addresses (which I will need to re-hard-code). New configuration needed to allow the routing:

# jcu01 - run
# ./jungfrauDetectorServer_virtual -p 2000
# ./jungfrauDetectorServer_virtual -p 2010
hostname 192.168.200.200:2000+192.168.200.200:2010+

# gh01 - run slsMultiReceiver 3000 2 0
rx_hostname 192.168.200.201:3000+192.168.200.201:3001+

0:udp_srcip 192.168.200.200
0:udp_dstip 192.168.200.201
0:udp_dstport 30000

0:udp_srcip2 192.168.200.200
0:udp_dstip2 192.168.200.201
0:udp_dstport2 30001

1:udp_srcip 192.168.200.200
1:udp_dstip 192.168.200.201
1:udp_dstport 30010

1:udp_srcip2 192.168.200.200
1:udp_dstip2 192.168.200.201
1:udp_dstport2 30011

numinterfaces 2

rx_zmqfreq 1
rx_zmqhwm 50000
rx_zmqstream 1

temp_control 1
temp_threshold 55

# exposure time, cycle time to use
exptime 0.0005
period 0.0005
frames 1000

# enable both network channels
readoutspeed full_speed

# save binary data (112 byte header / frame)
fformat binary
fwrite 1
fpath /dev/shm/gw

powerchip 1
```

N.B. be sure to enable jumbo frames on both ends i.e. `ifconfig <interface> mtu 9000`.

Should result in something like:

```
- 09:03:12.961 INFO: [30000]:  Packet_Loss:0 (0%)  Used_Fifo_Max_Level:0 	Free_Slots_Min_Level:2499 	Current_Frame#:11001
- 09:03:12.961 INFO: [30001]:  Packet_Loss:0 (0%)  Used_Fifo_Max_Level:0 	Free_Slots_Min_Level:2499 	Current_Frame#:11001
- 09:03:13.079 INFO: [30010]:  Packet_Loss:0 (0%)  Used_Fifo_Max_Level:0 	Free_Slots_Min_Level:2499 	Current_Frame#:11001
- 09:03:13.079 INFO: [30011]:  Packet_Loss:0 (0%)  Used_Fifo_Max_Level:0 	Free_Slots_Min_Level:2499 	Current_Frame#:11001
- 09:03:13.080 INFO: Stopping Receiver
- 09:03:13.080 INFO: Status: Transmitting
- 09:03:13.080 INFO: Stopping Receiver
- 09:03:13.080 INFO: Status: Transmitting
- 09:03:13.080 INFO: Shut down of UDP port 30000
- 09:03:13.081 INFO: Shut down of UDP port 30010
- 09:03:13.081 INFO: Shut down of UDP port 30001
- 09:03:13.081 INFO: Shut down of UDP port 30011
- 09:03:13.091 INFO: Closed UDP port 30000
- 09:03:13.091 INFO: Closed UDP port 30001
- 09:03:13.091 INFO: Closed UDP port 30010
- 09:03:13.091 INFO: Closed UDP port 30011
- 09:03:13.091 INFO: Master File: /dev/shm/gw/run_master_1.json
- 09:03:13.096 INFO: Status: finished
- 09:03:13.096 INFO: Summary of Port 30010
	Missing Packets		: 0
	Complete Frames		: 10000
	Last Frame Caught	: 11000
- 09:03:13.096 INFO: Summary of Port 30011
	Missing Packets		: 0
	Complete Frames		: 10000
	Last Frame Caught	: 11000
- 09:03:13.096 INFO: Receiver Stopped
- 09:03:13.096 INFO: Status: finished
- 09:03:13.096 INFO: Status: idle
- 09:03:13.096 INFO: Summary of Port 30000
	Missing Packets		: 0
	Complete Frames		: 10000
	Last Frame Caught	: 11000
- 09:03:13.096 INFO: Summary of Port 30001
	Missing Packets		: 0
	Complete Frames		: 10000
	Last Frame Caught	: 11000
- 09:03:13.096 INFO: Receiver Stopped
- 09:03:13.096 INFO: Status: idle
- 09:03:13.096 INFO: File Index: 2
- 09:03:13.096 INFO: File Index: 2
```
