###############################################################################
# sender.py
# Name: Murphy Cheng
# JHED ID: 1800017781
###############################################################################

import sys
import socket
import random
import datetime

from util import *

# packet size
MAX_PACKET_SIZE = 1400
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

def sender(receiver_ip, receiver_port, sender_port, window_size):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((receiver_ip, sender_port))

    # build RTP connection
    init_seq_num = 0
    seq_num = 0
    pkt_header = PacketHeader(type=START, seq_num=seq_num, length=0)
    pkt_header.checksum = compute_checksum(pkt_header) & 0xfffffff
    s.sendto(str(pkt_header), (receiver_ip, receiver_port))
    seq_num += 1

    # receive ack packet
    ack, address = s.recvfrom(BUFFER_SIZE)
    while address[0] != receiver_ip or address[1] != receiver_port:
        print("Not ack")
        ack, address = s.recvfrom(BUFFER_SIZE)

    # extract head and check checksum
    ack = PacketHeader(ack[:16])
    ack_checksum = ack.checksum
    ack.checksum = 0
    checksum = compute_checksum(ack) & 0xfffffff
    if checksum != ack_checksum:
        print(checksum, ack_checksum)
        print("ack checksum not match")
    
    print("Sender connection established")

    # divide data into packets
    while True:
        msg = input()
        msg = bytearray(msg)
        packets = []
        i = 0
        while i < len(msg):
            packet_header = PacketHeader(type=DATA, seq_num = seq_num, length=(min(i+MAX_PACKET_SIZE, len(msg)) - i))
            packet_header.checksum = compute_checksum(packet_header / msg[i:min(i+MAX_PACKET_SIZE, len(msg))]) & 0xfffffff
            packets.append(packet_header / msg[i:min(i+MAX_PACKET_SIZE, len(msg))])
            i += MAX_PACKET_SIZE
            seq_num += 1

        # sliding window
        window_start = 0
        window_end = min(window_start + window_size, len(packets))
        last_sent = -1
        flag = True
        while True:
            try:
                while True:
                    for i in range(last_sent + 1, window_end):
                        print('sent ', i)
                        s.sendto(str(packets[i]), (receiver_ip, receiver_port))
                        
                    last_sent = window_end - 1 + init_seq_num
                        
                    ack, addr = s.recvfrom(BUFFER_SIZE)
                    ack_header = PacketHeader(ack[:16])
                    print(ack_header.seq_num)
                    if addr[0] != receiver_ip or addr[1] != receiver_port:
                        print("not proper ack")
                    ack_checksum = ack_header.checksum
                    ack_header.checksum = 0
                    computed_checksum = compute_checksum(ack_header) & 0xfffffff
                    if computed_checksum != ack_checksum:
                        print(computed_checksum, ack_checksum)
                        print("Wrong checksum")
                    if ack_header.seq_num == PacketHeader(bytes(packets[window_start])[:16]).seq_num:
                        window_start += 1
                        window_end = min(window_start + window_size, len(packets) + init_seq_num + 1)
                        if window_start == len(packets):
                            flag = False
                            break
                        s.settimeout(0.5)
            except socket.timeout:
                print("timeout")
                last_sent = window_start - 1
            
            if flag == False:
                break

        print("Sent!")

    # end transport data, now end connection
    end_header = PacketHeader(type=END, seq_num=seq_num, length=0)
    end_header.checksum = compute_checksum(end_header)
    s.sendto(str(end_header), (receiver_ip, receiver_port))


def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, 6489, window_size)

if __name__ == "__main__":
    main()
