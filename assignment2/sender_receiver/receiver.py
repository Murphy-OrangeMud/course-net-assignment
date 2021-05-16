###############################################################################
# receiver.py
# Name: Murphy Cheng
# JHED ID: 1800017781
###############################################################################

import sys
import socket

from util import *

BUFFER_SIZE = 2048

# type
START = 0
END = 1
DATA = 2
ACK = 3

# PacketHeader:
# int type; // 0: START; 1: END; 2: DATA; 3: ACK
# int seq_num; // Described below
# int length; // Length of data; 0 for ACK, START and END packets
# int checksum; // 32-bit CRC

def receiver(sender_port, receiver_port, window_size):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    
    start, address = s.recvfrom(BUFFER_SIZE)
    start = PacketHeader(start[:16])
    recv_seq = start.seq_num
    
    ack_header = PacketHeader(type=ACK, seq_num=recv_seq, length=0)
    ack_header.checksum = compute_checksum(ack_header) & 0xfffffff
    s.sendto(str(ack_header), ('127.0.0.1', sender_port))
    recv_seq += 1

    print("Receiver connection established")
    message = bytearray()

    while True:
        # receive packet
        pkt, address = s.recvfrom(BUFFER_SIZE)
        print(pkt)

        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg) & 0xfffffff
        if pkt_checksum != computed_checksum:
            print(pkt_checksum, computed_checksum)
            print("checksums not match")
        if pkt_header.seq_num != recv_seq:
            print(pkt_header.seq_num, recv_seq)
            print("invalid packet seq num")
            continue
        if pkt_header.type == START or pkt_header.type == ACK:
            print("not data")
            continue
        if pkt_header.type == END:
            print("end")
            break

        ack_header = PacketHeader(type=ACK, seq_num=recv_seq, length=0)
        ack_header.checksum = compute_checksum(ack_header) & 0xfffffff
        s.sendto(str(ack_header), ('127.0.0.1', sender_port))
        
        print(msg)
        recv_seq += 1
        message += msg

    print(message)

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(6489, receiver_port, window_size)

if __name__ == "__main__":
    main()
