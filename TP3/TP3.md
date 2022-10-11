Geoffrey Diederichs B1 B
# TP3 : On va router des trucs
## I. ARP
### 1. Echange ARP
🌞**Générer des requêtes ARP**
- John :
```
$ ip a

2: enp0s8: 
    link/ether 08:00:27:4c:a8:54
    inet 192.168.57.2/24
```
- Marcel : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:64:5a:9f
    inet 192.168.57.3/24
```
```
$ ping 1920.168.57.2 -c 5

ping: 1920.168.57.2: Name or service not known
[rocky@localhost ~]$ ping 192.168.57.2 -c 5
PING 192.168.57.2 (192.168.57.2) 56(84) bytes of data.
64 bytes from 192.168.57.2: icmp_seq=1 ttl=64 time=0.605 ms
64 bytes from 192.168.57.2: icmp_seq=2 ttl=64 time=0.979 ms
64 bytes from 192.168.57.2: icmp_seq=3 ttl=64 time=0.695 ms
64 bytes from 192.168.57.2: icmp_seq=4 ttl=64 time=0.847 ms
64 bytes from 192.168.57.2: icmp_seq=5 ttl=64 time=1.23 ms

--- 192.168.57.2 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4096ms
rtt min/avg/max/mdev = 0.605/0.871/1.230/0.220 ms
```
- John : 
```
$ ip n s

192.168.57.1 dev enp0s8 lladdr 0a:00:27:00:00:01 DELAY
192.168.57.3 dev enp0s8 lladdr 08:00:27:64:5a:9f STALE
```
Adresse mac de Marcel : 08:00:27:64:5a:9f
- Marcel : 
```
$ ip n s

192.168.57.1 dev enp0s8 lladdr 0a:00:27:00:00:01 DELAY
192.168.57.2 dev enp0s8 lladdr 08:00:27:4c:a8:54 STALE
```
Adresse mac de John : 08:00:27:4c:a8:54
### 2. Analyse de trames
🌞**Analyse de trames**
```
$ sudo ip n f all
```
- John : 
```
sudo tcpdump -i enp0s8 -c 2 -w tp2_arp.pcap not port 22
```
- Marcel : 
```
ping 192.168.57.2
```
[Trames arp](./Trames/tp3_arp.pcap)
## II. Routage
### 1. Mise en place du routage
🌞**Activer le routage sur le noeud `router`**
- Routeur :
```
$ sudo firewall-cmd --list-all

public (active)
  interfaces: enp0s8 enp0s9
  forward: yes
  masquerade: yes
```
🌞**Ajouter les routes statiques nécessaires pour que `john` et `marcel` puissent se `ping`**
- Routeur : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:f5:f8:e6
    inet 192.168.57.254/24
3: enp0s9:
    link/ether 08:00:27:ca:c3:88
    inet 192.168.58.254/24
```
- John : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:3c:a5:2d
    inet 192.168.57.2/24
    
$ sudo ip r add 192.168.58.0/24 via 192.168.57.254
$ ip r s

192.168.57.0/24 dev enp0s8 proto kernel scope link src 192.168.57.2 
192.168.58.0/24 via 192.168.57.254 dev enp0s8
```
- Marcel : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:78:2b:57
    inet 192.168.58.2/24

$ sudo ip r add 192.168.57.0/24 via 192.168.57.254
$ ip r s

192.168.57.0/24 via 192.168.58.254 dev enp0s8 
192.168.58.0/24 dev enp0s8 proto kernel scope link src 192.168.58.2

$ ping 192.168.57.2 -c 3

PING 192.168.57.2 (192.168.57.2) 56(84) bytes of data.
64 bytes from 192.168.57.2: icmp_seq=1 ttl=63 time=0.986 ms
64 bytes from 192.168.57.2: icmp_seq=2 ttl=63 time=1.24 ms
64 bytes from 192.168.57.2: icmp_seq=3 ttl=63 time=1.26 ms

--- 192.168.57.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 0.986/1.163/1.261/0.125 ms
```
### 2. Analyse de trames
🌞**Analyse des échanges ARP**
| ordre | type trame  | IP source | MAC source              | IP destination | MAC destination            |
|-------|-------------|-----------|-------------------------|----------------|----------------------------|
| 1     | Requête ARP | 192.168.57.2        | `John` `08:00:27:3c:a5:2d` | 192.168.57.254            | `Broadcast` `FF:FF:FF:FF:FF` |
| 2     | Réponse ARP | 192.168.57.254         | `Routeur` `08:00:27:f5:f8:e6`                      | 192.168.57.2              | `John` `08:00:27:3c:a5:2d`    |
| 3    | Ping        | 192.168.57.2        | `John` `08:00:27:3c:a5:2d`                     | 192.168.58.2              | `Routeur` `08:00:27:f5:f8:e6`     
| 4  | Requête ARP         | 192.168.58.254       | `Routeur` `08:00:27:ca:c3:88`                  |     192.168.58.2          |   `Broadcast` `FF:FF:FF:FF:FF` 
| 5  | Réponse ARP         | 192.168.58.2      | `Marcel` `08:00:27:78:2b:57`                   |     192.168.58.254          |   `Routeur` `08:00:27:ca:c3:88`   |
| 6    | Ping        |      192.168.58.254   | `Routeur` `08:00:27:ca:c3:88`                       | 192.168.58.2            | `Marcel` `08:00:27:78:2b:57`                         |
| 7    | Pong        | 192.168.58.2            | `Marcel` `08:00:27:78:2b:57`                          | 192.168.58.254                       | `Routeur` `08:00:27:ca:c3:88`|
| 8 | Pong | 192.168.58.2 | `Routeur` `08:00:27:f5:f8:e6`    | 192.168.57.2 | `John` `08:00:27:3c:a5:2d` |

[Trames routeur sur l'interface enp0s8](./Trames/tp3_routage_routeur.pcapng)

[Trames Marcel](./Trames/tp3_routage_marcel.pcapng)

### 3. Accès internet

🌞**Donnez un accès internet à vos machines**
- John : 
```
$ sudo ip r add default via 192.168.57.254 dev enp0s8
$ ping 8.8.8.8 -c 1

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=23.0 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 23.039/23.039/23.039/0.000 ms
```
- Marcel : 
```
$ sudo ip r add default via 192.168.58.254 dev enp0s8
$ ping 8.8.8.8 -c 1

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=22.9 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 22.860/22.860/22.860/0.000 ms
```
```
$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 19235
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		216	IN	A	142.250.178.142

;; Query time: 27 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Oct 10 23:03:51 CEST 2022
;; MSG SIZE  rcvd: 55

$ ping google.com -c 1

PING google.com (216.58.214.78) 56(84) bytes of data.
64 bytes from par10s39-in-f14.1e100.net (216.58.214.78): icmp_seq=1 ttl=61 time=19.6 ms

--- google.com ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 19.609/19.609/19.609/0.000 ms
```

🌞**Analyse de trames**

| ordre | type trame | IP source          | MAC source              | IP destination | MAC destination |
|-------|------------|--------------------|-------------------------|----------------|-----------------|
| 1     | ping       | `John` `192.168.57.2` | `John` `08:00:27:3c:a5:2d` | `8.8.8.8`      | `Routeur` `08:00:27:f5:f8:e6`|
| 2     | pong       | `8.8.8.8`               |      `Routeur` `08:00:27:f5:f8:e6`                |      `John` `192.168.57.2`      | `John` `08:00:27:3c:a5:2d`             |

[Ping](./Trames/tp3_routage_internet.pcap)

## III. DHCP
### 1. Mise en place du serveur DHCP
🌞**Sur la machine `john`, vous installerez et configurerez un serveur DHCP** 
- Bob :
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:38:1c:9e
```
- John :
```
$ sudo dnf install dhcp-server
$ sudo cat /etc/dhcp/dhcpd.conf

default-lease-time 900;
max-lease-time 10800;
ddns-update-style none;
authorative;
subnet 192.168.57.0 netmask 255.255.255.0 {
	range 192.168.57.3 192.168.57.253;
	option routers 192.168.57.254;
	option subnet-mask 255.255.255.0;
	option domain-name-servers 8.8.8.8;
}

$ sudo firewall-cmd --permanent --add-port=67/udp
$ sudo systemctl enable --now dhcpd
$ sudo systemctl status dhcpd

● dhcpd.service - DHCPv4 Server Daemon
     Loaded: loaded (/usr/lib/systemd/system/dhcpd.service; enabled; vendor preset: disabled)
     Active: active (running) since Tue 2022-10-11 00:38:21 CEST; 14s ago
       Docs: man:dhcpd(8)
             man:dhcpd.conf(5)
   Main PID: 1212 (dhcpd)
     Status: "Dispatching packets..."
      Tasks: 1 (limit: 5908)
     Memory: 4.7M
        CPU: 8ms
     CGroup: /system.slice/dhcpd.service
             └─1212 /usr/sbin/dhcpd -f -cf /etc/dhcp/dhcpd.conf -user dhcpd -group dhcpd --no-pid

Oct 11 00:38:21 localhost.localdomain dhcpd[1212]: Wrote 0 leases to leases file.
Oct 11 00:38:21 localhost.localdomain dhcpd[1212]: Listening on LPF/enp0s8/08:00:27:3c:a5:2d/192.168.57.0/24
Oct 11 00:38:21 localhost.localdomain dhcpd[1212]: Sending on   LPF/enp0s8/08:00:27:3c:a5:2d/192.168.57.0/24
Oct 11 00:38:21 localhost.localdomain dhcpd[1212]: Sending on   Socket/fallback/fallback-net
Oct 11 00:38:21 localhost.localdomain dhcpd[1212]: Server starting service.
Oct 11 00:38:21 localhost.localdomain systemd[1]: Started DHCPv4 Server Daemon.
Oct 11 00:38:29 localhost.localdomain dhcpd[1212]: DHCPDISCOVER from 08:00:27:38:1c:9e via enp0s8
Oct 11 00:38:30 localhost.localdomain dhcpd[1212]: DHCPOFFER on 192.168.57.3 to 08:00:27:38:1c:9e via enp0s8
Oct 11 00:38:30 localhost.localdomain dhcpd[1212]: DHCPREQUEST for 192.168.57.3 (192.168.57.2) from 08:00:27:38:1c:9e via enp0s8
Oct 11 00:38:30 localhost.localdomain dhcpd[1212]: DHCPACK on 192.168.57.3 to 08:00:27:38:1c:9e via enp0s8
```
- Bob : 
```
$ ip a

2: enp0s8:
    link/ether 08:00:27:38:1c:9e
    inet 192.168.57.3/24
```
🌞**Améliorer la configuration du DHCP**
- John :
```
$ sudo cat /etc/dhcp/dhcpd.conf

default-lease-time 900;
max-lease-time 10800;
ddns-update-style none;
authorative;
subnet 192.168.57.0 netmask 255.255.255.0 {
	range 192.168.57.3 192.168.57.253;
	option routers 192.168.57.254;
	option subnet-mask 255.255.255.0;
	option domain-name-servers 8.8.8.8;
}
```
- Bob : 
```
$ sudo systemctl restart NetworkManager
$ ip a

2: enp0s8:
    link/ether 08:00:27:38:1c:9e
    inet 192.168.57.3/24
    
$ ping 192.168.57.254 -c 1

PING 192.168.57.254 (192.168.57.254) 56(84) bytes of data.
64 bytes from 192.168.57.254: icmp_seq=1 ttl=64 time=0.756 ms

--- 192.168.57.254 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.756/0.756/0.756/0.000 ms

$ ip r s

default via 192.168.57.254 dev enp0s8 proto dhcp src 192.168.57.3 metric 100 
192.168.57.0/24 dev enp0s8 proto kernel scope link src 192.168.57.3 metric 100

$ ping 8.8.8.8 -c 1

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=16.9 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 16.919/16.919/16.919/0.000 ms

$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 33084
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		300	IN	A	142.250.201.174

;; Query time: 23 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Tue Oct 11 01:19:59 CEST 2022
;; MSG SIZE  rcvd: 55

$ ping google.com -c 1

PING google.com (142.250.179.78) 56(84) bytes of data.
64 bytes from par21s19-in-f14.1e100.net (142.250.179.78): icmp_seq=1 ttl=61 time=16.2 ms

--- google.com ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 16.162/16.162/16.162/0.000 ms
```
### 2. Analyse de trames
🌞**Analyse de trames**
- Bob :
```
$ sudo dhclient -r
$ sudo dhclient
$ ip a

2: enp0s8: 
	link/ether 08:00:27:38:1c:9e
    inet 192.168.57.3/24
    inet 192.168.57.173/24
```
[Trames DHCP](./Trames/tp3_dhcp.pcap)
