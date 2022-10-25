# TP4 : TCP, UDP et services réseau
Geoffrey Diederichs B1 B
# Sommaire

- [I. First steps](#i-first-steps)
- [II. Mise en place](#ii-mise-en-place)
  - [1. SSH](#1-ssh)
  - [2. Routage](#2-routage)
- [III. DNS](#iii-dns)
  - [1. Présentation](#1-présentation)
  - [2. Setup](#2-setup)
  - [3. Test](#3-test)


# I. First steps

🌞 **Déterminez, pour ces 5 applications, si c'est du TCP ou de l'UDP**
🌞 **Demandez l'avis à votre OS**

[Streaming netflix](./Trames/netflix.pcapng)
- IP destinataire : 92.90.254.205
- Port destinataire : 443
- Port source : 50124
```
$ ss -tup

Netid            State            Recv-Q            Send-Q                             Local Address:Port                           Peer Address:Port              Process                                         
tcp              ESTAB            0                 0                                   10.33.16.194:50124                         92.90.254.205:https              users:(("firefox",pid=7385,fd=114))  
```
[Discord](./Trames/discord.pcapng)
- IP destinataire : 162.159.129.233 ; 162.159.134.234
- Port destinataire : 443 ; 443
- Port source : 44128 ; 60542
```
$ ss -tup

Netid            State            Recv-Q            Send-Q                             Local Address:Port                            Peer Address:Port              Process                                        
tcp              ESTAB            0                 0                                   10.33.16.194:44128                        162.159.135.232:https              users:(("Discord",pid=8579,fd=27))            
tcp              ESTAB            0                 0                                   10.33.16.194:60542                        162.159.134.234:https              users:(("Discord",pid=8579,fd=29)) 
```
[Mise à jour système Linux](./Trames/linux_update.pcapng)
- IP destinataire : 134.109.228.1
- Port destinataire : 80
- Port source : 33128
```
$ ss -tup

Netid               State               Recv-Q               Send-Q                                    Local Address:Port                                  Peer Address:Port                 Process               
tcp                 ESTAB               0                    0                                          10.33.16.194:33128                                134.109.228.1:http                                     
```
[Microsoft Teams](./Trames/teams.pcapng)
- IP destinataire : 20.42.72.131 ; 20.190.159.72
- Port destinataire : 443 ; 443
- Port source : 57914 ; 40704
```
$ ss -tup

Netid            State            Recv-Q            Send-Q                             Local Address:Port                             Peer Address:Port              Process                                       
tcp              ESTAB            0                 0                                   10.33.16.194:40704                           20.190.159.72:https              users:(("teams",pid=11572,fd=33))   
tcp              ESTAB            0                 0                                   10.33.16.194:57914                            20.42.72.131:https              users:(("teams",pid=11572,fd=28))   
```
[Lichess](./Trames/lichess.pcapng)
- IP destinataire : 54.38.164.114 ; 37.187.205.99
- Port destinataire : 443 ; 443
- Port source : 48342 ; 57628
```
$ ss -tup

Netid            State            Recv-Q            Send-Q                             Local Address:Port                           Peer Address:Port             Process                                          
tcp              ESTAB            0                 0                                   10.33.16.194:48342                         54.38.164.114:https             users:(("firefox",pid=12129,fd=127))  
tcp              ESTAB            0                 0                                   10.33.16.194:57628                         37.187.205.99:https             users:(("firefox",pid=12129,fd=140))  
```
# II. Mise en place

## 1. SSH

🌞 **Examinez le trafic dans Wireshark**

[ssh](./Trames/ssh.pcapng)

🌞 **Demandez aux OS**

Depuis mon PC : 

```
$ ss -tup

Netid State      Recv-Q Send-Q       Local Address:Port      Peer Address:Port  Process    
tcp   ESTAB      0      0             192.168.57.1:55970     192.168.57.2:ssh    users:(("ssh",pid=3150,fd=3))   
```

Depuis node1.tp4.b1 : 

```
$ ss -tup

Netid                State                Recv-Q                Send-Q                                 Local Address:Port                                 Peer Address:Port                 Process                
tcp                  ESTAB                0                     0                                       192.168.57.2:ssh                                  192.168.57.1:55970
```
# III. DNS
## 2. Setup

```
$ sudo cat /etc/named.conf

//
// named.conf
//
// Provided by Red Hat bind package to configure the ISC BIND named(8) DNS
// server as a caching only nameserver (as a localhost DNS resolver only).
//
// See /usr/share/doc/bind*/sample/ for example named configuration files.
//

options {
	listen-on port 53 { 127.0.0.1; any; };
	listen-on-v6 port 53 { ::1; };
	directory 	"/var/named";
	dump-file 	"/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	memstatistics-file "/var/named/data/named_mem_stats.txt";
	secroots-file	"/var/named/data/named.secroots";
	recursing-file	"/var/named/data/named.recursing";
	allow-query     { localhost; any; };
	allow-query-cache { localhost; any; };

	/* 
	 - If you are building an AUTHORITATIVE DNS server, do NOT enable recursion.
	 - If you are building a RECURSIVE (caching) DNS server, you need to enable 
	   recursion. 
	 - If your recursive DNS server has a public IP address, you MUST enable access 
	   control to limit queries to your legitimate users. Failing to do so will
	   cause your server to become part of large scale DNS amplification 
	   attacks. Implementing BCP38 within your network would greatly
	   reduce such attack surface 
	*/
	recursion yes;

	dnssec-validation yes;

	managed-keys-directory "/var/named/dynamic";
	geoip-directory "/usr/share/GeoIP";

	pid-file "/run/named/named.pid";
	session-keyfile "/run/named/session.key";

	/* https://fedoraproject.org/wiki/Changes/CryptoPolicy */
	include "/etc/crypto-policies/back-ends/bind.config";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "tp4.b1" IN {
	type master;
	file "tp4.b1.db";
	allow-update { none; };
	allow-query { any; };
};

zone "1.4.10.in-addr.arpa" IN {
     type master;
     file "tp4.b1.rev";
     allow-update { none; };
     allow-query { any; };
};


include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
```
```
$ sudo cat /var/named/tp4.b1.db

$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

; Enregistrements DNS pour faire correspondre des noms à des IPs
dns-server IN A 192.168.57.4
node1      IN A 192.168.57.2
```
```
$ sudo cat /var/named/tp4.b1.db

$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

; Enregistrements DNS pour faire correspondre des noms à des IPs
dns-server IN A 192.168.57.4
node1      IN A 192.168.57.2
[rocky@dns-server ~]$ sudo cat /var/named/tp4.b1.rev
$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

;Reverse lookup for Name Server
4 IN PTR dns-server.tp4.b1.
2 IN PTR node1.tp4.b1.
```
```
$ systemctl status named

● named.service - Berkeley Internet Name Domain (DNS)
     Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; vendor preset: disabled)
     Active: active (running) since Tue 2022-10-25 13:56:02 CEST; 8min ago
   Main PID: 1048 (named)
      Tasks: 5 (limit: 5908)
     Memory: 18.9M
        CPU: 70ms
     CGroup: /system.slice/named.service
             └─1048 /usr/sbin/named -u named -c /etc/named.conf

Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: zone 1.0.0.127.in-addr.arpa/IN: loaded serial 0
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: network unreachable resolving './NS/IN': 192.58.128.30#53
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: network unreachable resolving './DNSKEY/IN': 198.41.0.4#>
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: network unreachable resolving './NS/IN': 198.41.0.4#53
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: resolver priming query complete
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: zone localhost.localdomain/IN: loaded serial 0
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: managed-keys-zone: Unable to fetch DNSKEY set '.': failu>
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: all zones loaded
Oct 25 13:56:02 dns-server.tp4.b1 systemd[1]: Started Berkeley Internet Name Domain (DNS).
Oct 25 13:56:02 dns-server.tp4.b1 named[1048]: running
```
🌞 **Ouvrez le bon port dans le firewall**
```
$ sudo ss -ap '( sport = :53 )'

Netid             State              Recv-Q             Send-Q                          Local Address:Port                             Peer Address:Port             Process                                       
udp               UNCONN             0                  0                                192.168.57.4:domain                                0.0.0.0:*                 users:(("named",pid=1048,fd=19))             
udp               UNCONN             0                  0                                   127.0.0.1:domain                                0.0.0.0:*                 users:(("named",pid=1048,fd=16))             
udp               UNCONN             0                  0                                       [::1]:domain                                   [::]:*                 users:(("named",pid=1048,fd=22))             
tcp               LISTEN             0                  10                               192.168.57.4:domain                                0.0.0.0:*                 users:(("named",pid=1048,fd=21))             
tcp               LISTEN             0                  10                                  127.0.0.1:domain                                0.0.0.0:*                 users:(("named",pid=1048,fd=17))             
tcp               LISTEN             0                  10                                      [::1]:domain                                   [::]:*                 users:(("named",pid=1048,fd=23))                                          
```
```
$ sudo firewall-cmd --add-port=53/udp
$ sudo firewall-cmd --add-port=53/udp --permanent
$ sudo firewall-cmd --add-port=53/fdp
$ sudo firewall-cmd --add-port=53/fdp --permanent
$ sudo firewall-cmd --list-all

public (active)
  ports: 53/tcp 53/udp
```
## 3. Test
🌞 **Sur la machine `node1.tp4.b1`**

```
[rocky@node1 ~]$ dig node1.tp4.b1

; <<>> DiG 9.16.23-RH <<>> node1.tp4.b1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 11066
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 125ed1bf07ce2f89010000006357da059bee8b4c02bf8db5 (good)
;; QUESTION SECTION:
;node1.tp4.b1.			IN	A

;; ANSWER SECTION:
node1.tp4.b1.		86400	IN	A	192.168.57.2

;; Query time: 2 msec
;; SERVER: 192.168.57.4#53(192.168.57.4)
;; WHEN: Tue Oct 25 14:33:55 CEST 2022
;; MSG SIZE  rcvd: 85

[rocky@node1 ~]$ dig dns-server.tp4.b1

; <<>> DiG 9.16.23-RH <<>> dns-server.tp4.b1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 54390
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 97b0f157f73a60a6010000006357da42451c5392c82b8bcd (good)
;; QUESTION SECTION:
;dns-server.tp4.b1.		IN	A

;; ANSWER SECTION:
dns-server.tp4.b1.	86400	IN	A	192.168.57.4

;; Query time: 0 msec
;; SERVER: 192.168.57.4#53(192.168.57.4)
;; WHEN: Tue Oct 25 14:34:57 CEST 2022
;; MSG SIZE  rcvd: 90

```

```
[rocky@dns-server ~]$ sudo cat /etc/named.conf

[...]

zone "com" IN {
	type master;
	file "com.db";
	allow-update { none; };
	allow-query { any; };
};

$ sudo cat /var/named/com.db

$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

; Enregistrements DNS pour faire correspondre des noms à des IPs
google IN A 142.250.179.78

[rocky@dns-server ~]$ sudo systemctl restart named
```
```
[rocky@node1 ~]$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 31236
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: a6e5cb820c29459c010000006357db71bac8573c921ce4b6 (good)
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		86400	IN	A	142.250.179.78

;; Query time: 1 msec
;; SERVER: 192.168.57.4#53(192.168.57.4)
;; WHEN: Tue Oct 25 14:40:00 CEST 2022
;; MSG SIZE  rcvd: 83
```
🌞 **Sur votre PC**

```
$ cat /etc/resolv.conf

# Generated by NetworkManager
nameserver 192.168.57.4

$  dig google.com

; <<>> DiG 9.18.7 <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 37769
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: c0aa6e5c2d2264de010000006357dcb0aff9df45656c1b75 (good)
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		86400	IN	A	142.250.179.78

;; Query time: 0 msec
;; SERVER: 192.168.57.4#53(192.168.57.4) (UDP)
;; WHEN: Tue Oct 25 14:58:58 CEST 2022
;; MSG SIZE  rcvd: 83
```

[DNS](./Trames/ssh.pcapng)
