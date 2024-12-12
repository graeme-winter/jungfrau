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

```
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

## Simulator Enhancements

Want to be able to read data in to the simulator to transmit, either generated from Eiger data by performing an "[inverse correction](./PIXEL_SIMULATION.md)" or data captured from a real JUNGFRAU data collection.

The simulator is built around simulating _modules_ i.e. one simulator tries to generate the data for one module of 512x1024 pixels. The construction of the header is pretty basic, and done in a tight loop, and (by default) different for every pixel which is very expensive and prevents the system from going at full speed. In addition, there are issues with the way that the delays are calculated.

Improvements proposed:

- produce the chunks on a cleaner clock i.e. compute the times when these should be emitted at the _start_ of the scan then for each frame, wait until that time has passed
- pre-compute data for emission, assuming enough memory is available. For one of the old com15 nodes we have ~40GB of memory free, which at 1MB / frame should allow for ~20k frames - looping this though is fine so really only need ~3600 frames or something then re-transmit
- pre-computing most of the header then just updating a single frame counter seems easy

Will work towards these in a branch of the slsDetector package.

## Simulator Machines

We have:

- 4 x com15 node each with 2 x 40GbE
- 1 x JCU

to use for driving the simulation. Need to map IP addresses to module / ports =>

Machine:

|        | Column 0 | Column 1 | Column 2 |
|--------|----------|----------|----------|
| Row 0  |   JTU1   |   JTU2   |   JTU3   |
| Row 1  |   JTU1   |   JTU2   |   JTU3   |
| Row 2  |   JTU1   |   JCU    |   JTU4   |
| Row 3  |   JTU1   |   JCU    |   JTU4   |
| Row 4  |   JTU2   |   JTU3   |   JTU4   |
| Row 5  |   JTU2   |   JTU3   |   JTU4   |

Here the first two "JTU" entries are on one interface, the second two on the other interface, and the first of these on one port, the second on another port, so need to map all the ports and interfaces correctly to have this work _right_.

Machine network / IP address hard coding:

| Machine | Interface |   IP Addresss   |
|---------|-----------|-----------------|
| jcu01   | p5p2      | 192.168.200.200 |
| jtu-01  | p2p1      | 192.168.200.211 |
| jtu-01  | p2p2      | 192.168.200.221 |
| jtu-02  | p2p1      | 192.168.200.212 |
| jtu-02  | p2p2      | 192.168.200.222 |
| jtu-03  | p2p1      | 192.168.200.213 |
| jtu-03  | p2p2      | 192.168.200.223 |
| jtu-04  | p2p1      | 192.168.200.214 |
| jtu-05  | p2p2      | 192.168.200.224 |

All on `/255` mask, with settings kin to

```
5: p5p2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP group default qlen 1000
    link/ether 98:03:9b:89:c1:a7 brd ff:ff:ff:ff:ff:ff
    altname enp134s0f1
    inet 192.168.200.200/24 brd 192.168.200.255 scope global noprefixroute p5p2
       valid_lft forever preferred_lft forever
    inet6 fe80::9a03:9bff:fe89:c1a7/64 scope link
       valid_lft forever preferred_lft forever
```

## 9M Simulation

This needs a [long config file](../005-simulator-config/9m-simulator.conf) but works correctly - if slowly. Also depends on using a modified version of the virtual server hacked around [in a fork of the repo](https://github.com/graeme-winter/slsDetectorPackage/pull/1) - it fails if you try to run at 1kHz which should in theory fit inside the available network switches.

## 2M Simulation

### 2M from one machine, two interfaces

This also fails at full speed from one machine, using two full interfaces. To reproduce this failure:

1. ssh into i24-jtu-01, run 4 login sessions, each will run one full module of the simulation - run as `jungfrauDetectorServer_virtual -p PORT` where `PORT` is 2020, 2030, 2040, 2050 (as configured in the 2M configuration file.)
2. ssh into bl24i-sc-gh-01, run `slsMultiReceiver 3000 4 0` - this will spin up four receivers which will be configured with... (watch the output of this window for errors)

At this point the desktop may look like:

![Desktop image](./simulator-desktop.png)

3. on an i24 machine run `sls_detector_put config ~/git/jungfrau/005-simulator-config/2m-simulator-1.conf` This will produce a lot of output... you can then trigger acquisition with `sls_detector_acquire` which should work fine at 1000Hz (1.0 / (period + exptime)). Lowering the exposure time and period is sufficient with e.g. `sls_detector_put period 0.00025` is enough to trigger packet loss...

### 2M from two machines, one interface on each

Since a 1M works fine, we should be able to do a 1M from two machines, right? Yes, yes we can. This bodes well. You need to apply some diffs to the 2M config tho:

```
< hostname 192.168.200.211:2020+192.168.200.211:2030+192.168.200.212:2040+192.168.200.212:2050+
---
> hostname 192.168.200.211:2020+192.168.200.211:2030+192.168.200.221:2020+192.168.200.221:2030+
27c27
< 2:udp_srcip 192.168.200.212
---
> 2:udp_srcip 192.168.200.221
31c31
< 2:udp_srcip2 192.168.200.212
---
> 2:udp_srcip2 192.168.200.221
35c35
< 3:udp_srcip 192.168.200.212
---
> 3:udp_srcip 192.168.200.221
39c39
< 3:udp_srcip2 192.168.200.212
---
> 3:udp_srcip2 192.168.200.221
```

Once you are used to configuring these beasties, this is not really confusing: we are just pointing to the interfaces on the machines. This makes me think that the machines are not powerful enough to drive 80Gb/s out.
