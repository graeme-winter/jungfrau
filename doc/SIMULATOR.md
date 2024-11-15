# Jungfrau Simulator

The [SLS detector software](https://slsdetectorgroup.github.io/devdoc/) includes simulators which can be used to simulate the behaviour of the detectors. These are available if you compile the code with `SLS_USE_SIMULATOR=ON` i.e.

```
git clone git@github.com:slsdetectorgroup/slsDetectorPackage.git
mkdir slsDetectorPackage-build
cd slsDetectorPackage-build
cmake -DSLS_USE_SIMULATOR=ON ../slsDetectorPackage
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
