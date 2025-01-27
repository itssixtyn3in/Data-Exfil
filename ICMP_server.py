from scapy.all import sniff, IP, ICMP

def icmp_packet_callback(packet):
    if packet.haslayer(ICMP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        raw_payload = packet[ICMP].payload.load if hasattr(packet[ICMP].payload, 'load') else None
        print(f"ICMP Packet Captured:")
        print(f"  Source: {ip_src}")
        print(f"  Destination: {ip_dst}")
        if raw_payload:
            print(f"  Payload: {raw_payload.decode('utf-8', errors='ignore')}")
        print("-" * 50)

if __name__ == "__main__":
    print("Listening for ICMP packets...")
    sniff(filter="icmp", prn=icmp_packet_callback, store=0)
