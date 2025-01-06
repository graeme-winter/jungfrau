# Jungfrau Emulator Configuration

The details of all the configs, because some of them are manually applied and will want to be re-applied.

## Grace Hopper Box bl24i-sc-gh-01

Network interfaces are not currentlty correctly configured on start up because I could not figure out the network configuration YAML nonsense. TODO. The key interfaces to configure are the two 100GbE interfaces on the ConnectX-7 card:

```console
graeme@bl24i-sc-gh-01:~$ ip address show dev enp1s0f0np0 
2: enp1s0f0np0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP group default qlen 1000
    link/ether a0:88:c2:d5:84:b2 brd ff:ff:ff:ff:ff:ff
    inet 192.168.202.201/24 brd 192.168.202.255 scope global enp1s0f0np0
       valid_lft forever preferred_lft forever
    inet6 fe80::a288:c2ff:fed5:84b2/64 scope link 
       valid_lft forever preferred_lft forever
graeme@bl24i-sc-gh-01:~$ ip address show dev enp1s0f1np1
4: enp1s0f1np1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP group default qlen 1000
    link/ether a0:88:c2:d5:84:b3 brd ff:ff:ff:ff:ff:ff
    inet 192.168.201.201/24 brd 192.168.201.255 scope global enp1s0f1np1
       valid_lft forever preferred_lft forever
    inet6 fe80::a288:c2ff:fed5:84b3/64 scope link 
       valid_lft forever preferred_lft forever
```

with routing:

```console
graeme@bl24i-sc-gh-01:~$ ip r
192.168.201.0/24 dev enp1s0f1np1 proto kernel scope link src 192.168.201.201 
192.168.202.0/24 dev enp1s0f0np0 proto kernel scope link src 192.168.202.201 
192.168.203.0/24 via 192.168.201.254 dev enp1s0f1np1 
192.168.204.0/24 via 192.168.202.254 dev enp1s0f0np0 
```

(these are the extra lines I needed to add to sort out the rouging correctly.) This should be enough? Provided that jumbo packets are enabled. In `/etc/sysctl.conf` also need some extra lines:

```console
net.core.rmem_max = 1048576000
net.core.rmem_default= 1048576000
net.core.netdev_max_backlog = 250000
```

These essentially make for a lot more headroom. N.B. need something similar on the transmitting nodes.

## JCU box bl24i-sc-jcu01

This box was originally configured to capture data from the real JUNGFRAU 1M detector but here we are using it as one of the sources of packets. Company RHEL8 box so much easier to manage the network configuration, which is all in `/etc/sysconfig/network-scripts/`. This only has a single 40GbE link, so

```console
bl24i-sc-jcu01 network-scripts :) $ cat ifcfg-p5p2
DEVICE=p5p2
# 40g Fibre for detector
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.200.200
NETMASK=255.255.255.0
USERCTL=yes
MTU=9000
ETHTOOL_OPTS="autoneg off speed 40000 duplex full"
```

Interestingly, this would appear to be out of date:

```console
5: p5p2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP group default qlen 1000
    link/ether 98:03:9b:89:c1:a7 brd ff:ff:ff:ff:ff:ff
    altname enp134s0f1
    inet 192.168.203.200/24 brd 192.168.203.255 scope global noprefixroute p5p2
       valid_lft forever preferred_lft forever
    inet6 fe80::9a03:9bff:fe89:c1a7/64 scope link 
       valid_lft forever preferred_lft forever
```

is the correct configuration, with, of course, routing:

```console
192.168.201.0/24 via 192.168.203.254 dev p5p2 
192.168.202.0/24 via 192.168.203.254 dev p5p2 
192.168.203.0/24 dev p5p2 proto kernel scope link src 192.168.203.200 metric 102 
192.168.204.0/24 via 192.168.203.254 dev p5p2 
```

This corresponds to the configuration on the switch, so it is important that the right VLAN / subnet is used. This is universal advice: I should label which cables plug into which sockets, perhaps with some coloured stickers. For the transmission machines we also need to have a hefty UDP transmission buffer:

```console
sudo sysctl -w net.core.wmem_default=134217728
```

Again, this corresponds to all the machines.

## JTU 01 to 04 i24-jtu-0{1...4}

These are repurposed com15 cluster nodes which have two socket 40GbE cards, with the following configuration (which _does_ appear on reboot)

```console
i24-jtu-01 network-scripts :) $ cat ifcfg-p2p1
DEVICE=p2p1
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.203.201
NETMASK=255.255.255.0
USERCTL=yes
MTU=9000
# ETHTOOL_OPTS="autoneg off speed 40000 duplex full"
```

```console
i24-jtu-01 network-scripts :) $ cat ifcfg-p2p2
DEVICE=p2p2
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.204.201
NETMASK=255.255.255.0
USERCTL=yes
MTU=9000
# ETHTOOL_OPTS="autoneg off speed 40000 duplex full"
```

with this routing snippet

```console
i24-jtu-01 network-scripts :) $ ip r
192.168.201.0/24 via 192.168.203.254 dev p2p1 
192.168.202.0/24 via 192.168.204.254 dev p2p2 
192.168.203.0/24 dev p2p1 proto kernel scope link src 192.168.203.201 metric 101 
192.168.204.0/24 dev p2p2 proto kernel scope link src 192.168.204.201 metric 102 
```

The machines -02, -03, -04 have the last octet of the IP address mapped accordingly.
