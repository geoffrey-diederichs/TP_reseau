# B1 Réseau - TP1
Diederichs Geoffrey B1B
TP fait sur Manjaro

# TP1 - Premier pas réseau

# I. Exploration locale en solo

## 1. Affichage d'informations sur la pile TCP/IP locale

### En ligne de commande

**🌞 Affichez les infos des cartes réseau de votre PC**

- WiFi

```
~ ifconfig

wlp4s0:
        inet 10.33.16.187 
        ether d8:f3:bc:54:c7:8f
```
- Ethernet
```
~ ifconfig

enp3s0: 
        ether c0:18:50:0e:cb:bb
```
Pas d'adresse IP car je ne suis pas connecté à internet par ethernet.

**🌞 Affichez votre gateway**

```
~ ip route

default via 10.33.19.254
```

**🌞 Déterminer la MAC de la passerelle**

```
~ arp

Address                  HWtype  HWaddress                       
_gateway                 ether   00:c0:e7:e0:04:4e   

```

### En graphique (GUI : Graphical User Interface)

**🌞 Trouvez comment afficher les informations sur une carte IP (change selon l'OS)**

![](https://i.imgur.com/gwYKQ0n.png)


## 2. Modifications des informations

### A. Modification d'adresse IP (part 1)  

🌞 Utilisez l'interface graphique de votre OS pour **changer d'adresse IP** :

![](https://i.imgur.com/PRZRs7u.png)
![](https://i.imgur.com/jHN7NA1.png)



🌞 **Il est possible que vous perdiez l'accès internet.**

Par malchance je suis tombé sur une adresse IP déjà attribué, or le routeur n'accepte qu'une machine par adresse IP.


# II. Exploration locale en duo

## Création du réseau (oupa)

## 3. Modification d'adresse IP

🌞 **Modifiez l'IP des deux machines pour qu'elles soient dans le même réseau**

![](https://i.imgur.com/YPp4aJU.png)

🌞 **Vérifier à l'aide d'une commande que votre IP a bien été changée**
```
~ ip a

2: enp3s0: 
    inet 10.10.10.2/24
```
```
Carte Ethernet Ethernet :

   Suffixe DNS propre à la connexion. . . :
   Adresse IPv6 de liaison locale. . . . .: fe80::a0f0:514f:c687:c412%7
   Adresse IPv4. . . . . . . . . . . . . .: 10.10.10.1
   Masque de sous-réseau. . . . . . . . . : 255.255.255.0
   Passerelle par défaut. . . . . . . . . :

```
🌞 **Vérifier que les deux machines se joignent**

```
~ ping 10.10.10.1

PING 10.10.10.1 (10.10.10.1) 56(84) bytes of data.
64 bytes from 10.10.10.1: icmp_seq=119 ttl=128 time=2.40 ms
64 bytes from 10.10.10.1: icmp_seq=120 ttl=128 time=2.48 ms
64 bytes from 10.10.10.1: icmp_seq=121 ttl=128 time=2.45 ms
64 bytes from 10.10.10.1: icmp_seq=122 ttl=128 time=1.93 ms
64 bytes from 10.10.10.1: icmp_seq=123 ttl=128 time=2.16 ms
64 bytes from 10.10.10.1: icmp_seq=124 ttl=128 time=2.53 ms
64 bytes from 10.10.10.1: icmp_seq=125 ttl=128 time=2.65 ms
64 bytes from 10.10.10.1: icmp_seq=126 ttl=128 time=2.73 ms
64 bytes from 10.10.10.1: icmp_seq=127 ttl=128 time=2.40 ms
64 bytes from 10.10.10.1: icmp_seq=128 ttl=128 time=2.64 ms
64 bytes from 10.10.10.1: icmp_seq=129 ttl=128 time=2.57 ms
64 bytes from 10.10.10.1: icmp_seq=130 ttl=128 time=2.52 ms
^C
--- 10.10.10.1 ping statistics ---
130 packets transmitted, 12 received, 90.7692% packet loss, time 130598ms
rtt min/avg/max/mdev = 1.927/2.454/2.731/0.213 ms
```
```
>ping 10.10.10.2

Envoi d’une requête 'Ping'  10.10.10.2 avec 32 octets de données :
Réponse de 10.10.10.2 : octets=32 temps=4 ms TTL=64
Réponse de 10.10.10.2 : octets=32 temps=2 ms TTL=64
Réponse de 10.10.10.2 : octets=32 temps=2 ms TTL=64
Réponse de 10.10.10.2 : octets=32 temps=2 ms TTL=64
```

🌞 **Déterminer l'adresse MAC de votre correspondant**

- pour cela, affichez votre table ARP
```
~ arp

Address                  HWtype  HWaddress                     
10.10.10.1               ether   b4:45:06:7e:a1:3d                    

```

## 4. Utilisation d'un des deux comme gateway

🌞**Tester l'accès internet**

![](https://i.imgur.com/EfEvJqI.png)
```
~ ip a

2: enp3s0: 
    inet 192.168.137.2/24
```
```
~ ping 1.1.1.1

PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=54 time=21.4 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=54 time=21.7 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=54 time=22.6 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=54 time=21.1 ms
^C
--- 1.1.1.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 21.094/21.691/22.601/0.565 ms
```


🌞 **Prouver que la connexion Internet passe bien par l'autre PC**

```
~ traceroute 1.1.1.1

traceroute to 1.1.1.1 (1.1.1.1), 30 hops max, 60 byte packets
 1  _gateway (192.168.137.1)  1.000 ms  0.959 ms  0.941 ms
 2  * * *
 3  _gateway (10.33.19.254)  8.078 ms  8.063 ms  8.047 ms
 4  137.149.196.77.rev.sfr.net (77.196.149.137)  9.263 ms  9.247 ms  9.231 ms
 5  108.97.30.212.rev.sfr.net (212.30.97.108)  9.215 ms  9.199 ms  9.184 ms
 6  222.172.136.77.rev.sfr.net (77.136.172.222)  23.432 ms  24.416 ms  24.383 ms
 7  221.172.136.77.rev.sfr.net (77.136.172.221)  24.366 ms  23.280 ms  23.240 ms
 8  221.10.136.77.rev.sfr.net (77.136.10.221)  23.223 ms  22.025 ms  26.490 ms
 9  221.10.136.77.rev.sfr.net (77.136.10.221)  21.969 ms  21.954 ms  21.939 ms
10  141.101.67.254 (141.101.67.254)  21.923 ms  20.340 ms  20.718 ms
11  172.71.124.2 (172.71.124.2)  24.857 ms 172.71.116.2 (172.71.116.2)  24.840 ms 172.71.124.2 (172.71.124.2)  23.739 ms
12  one.one.one.one (1.1.1.1)  23.683 ms  23.665 ms  23.646 ms
```

## 5. Petit chat privé

🌞 **sur le PC *serveur***
```
~ netcat -l -p 8888

Coucouu
Hello
```
🌞 **sur le PC *client***

```
~ netcat 192.168.137.1 8888

er
coucojbdef
```


🌞 **Visualiser la connexion en cours**

```
~ ss -antp

State                   Recv-Q              Send-Q                                 
ESTAB                   0                   0                                 192.168.137.2:8888                                192.168.137.1:56914               users:(("netcat",pid=4284,fd=4))                 
                                          
```

## 6. Firewall

🌞 **Activez et configurez votre firewall**

```
~ sudo iptables -A OUTPUT -p icmp -j ACCEPT
~ sudo iptables -A INPUT -p icmp -j ACCEPT
~ sudo iptables -A INPUT -i eth0 -p tcp --dport 8888 -j ACCEPT
```
```
~ ping 192.168.137.1

PING 192.168.137.1 (192.168.137.1) 56(84) bytes of data.
64 bytes from 192.168.137.1: icmp_seq=39 ttl=128 time=0.657 ms
64 bytes from 192.168.137.1: icmp_seq=40 ttl=128 time=1.28 ms
64 bytes from 192.168.137.1: icmp_seq=41 ttl=128 time=0.661 ms
64 bytes from 192.168.137.1: icmp_seq=42 ttl=128 time=0.864 ms
64 bytes from 192.168.137.1: icmp_seq=43 ttl=128 time=0.648 ms
^C
--- 192.168.137.1 ping statistics ---
43 packets transmitted, 5 received, 88.3721% packet loss, time 42555ms

```
```
~ netcat -l -p 8888
    
heldeijd           
```
```
~ netcat 192.168.137.1 8888
    
hello
knjki     
```
  
# III. Manipulations d'autres outils/protocoles côté client

## 1. DHCP

🌞**Exploration du DHCP, depuis votre PC**
```
~ nmcli connection show "WiFi@YNOV" | grep -i dhcp4.option
    
DHCP4.OPTION[1]:                        dhcp_lease_time = 86336
DHCP4.OPTION[2]:                        dhcp_server_identifier = 10.33.19.254
DHCP4.OPTION[4]:                        expiry = 1664967143
```

## 2. DNS

🌞** Trouver l'adresse IP du serveur DNS que connaît votre ordinateur**
```
~ cat /etc/resolv.conf

# Generated by resolvconf
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
```

🌞 Utiliser, en ligne de commande l'outil `nslookup` (Windows, MacOS) ou `dig` (GNU/Linux, MacOS) pour faire des requêtes DNS à la main
```
~ dig www.google.com

; <<>> DiG 9.18.6 <<>> www.google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55724
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;www.google.com.			IN	A

;; ANSWER SECTION:
www.google.com.		31	IN	A	142.250.179.68

;; Query time: 23 msec
;; SERVER: 8.8.8.8#53(8.8.8.8) (UDP)
;; WHEN: Tue Oct 04 13:47:42 CEST 2022
;; MSG SIZE  rcvd: 59

```
```
~ dig www.ynov.com

; <<>> DiG 9.18.6 <<>> www.ynov.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 3736
;; flags: qr rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;www.ynov.com.			IN	A

;; ANSWER SECTION:
www.ynov.com.		300	IN	A	104.26.11.233
www.ynov.com.		300	IN	A	172.67.74.226
www.ynov.com.		300	IN	A	104.26.10.233

;; Query time: 143 msec
;; SERVER: 8.8.8.8#53(8.8.8.8) (UDP)
;; WHEN: Tue Oct 04 13:47:49 CEST 2022
;; MSG SIZE  rcvd: 89

```
Ynov possède plusieurs addresses IP auxquelles il nous renvoie pour répartir la charge. Google n'en affichant qu'une, le fait probablement derrière.
```
~ dig -x 231.34.113.12

; <<>> DiG 9.18.6 <<>> -x 231.34.113.12
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 42492
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;12.113.34.231.in-addr.arpa.	IN	PTR

;; AUTHORITY SECTION:
231.in-addr.arpa.	1640	IN	SOA	sns.dns.icann.org. noc.dns.icann.org. 2022091113 7200 3600 604800 3600

;; Query time: 33 msec
;; SERVER: 8.8.8.8#53(8.8.8.8) (UDP)
;; WHEN: Tue Oct 04 14:47:47 CEST 2022
;; MSG SIZE  rcvd: 112
```
```
~ dig -x 78.34.2.17
; <<>> DiG 9.18.6 <<>> -x 78.34.2.17
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 8438
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;17.2.34.78.in-addr.arpa.	IN	PTR

;; ANSWER SECTION:
17.2.34.78.in-addr.arpa. 2582	IN	PTR	cable-78-34-2-17.nc.de.

;; Query time: 26 msec
;; SERVER: 8.8.8.8#53(8.8.8.8) (UDP)
;; WHEN: Tue Oct 04 15:01:36 CEST 2022
;; MSG SIZE  rcvd: 88

```

# IV. Wireshark
## 1. Intro Wireshark
🌞 Utilisez le pour observer les trames qui circulent entre vos deux carte Ethernet. Mettez en évidence : 

- Ping :
![](https://i.imgur.com/LU6gMCg.png)
- Netcat :
![](https://i.imgur.com/7fvyiEw.png)
- Requête DNS : 
![](https://i.imgur.com/Q3dlYZ1.png)

## 2. Bonus : avant-goût TCP et UDP

🌞 **Wireshark it**
![](https://i.imgur.com/XjudzTQ.png)
- IP du serveur youtube : 
91.68.245.17
- Port du serveur youtube utilisé : 
443