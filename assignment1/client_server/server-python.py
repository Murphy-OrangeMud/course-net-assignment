###############################################################################
# server-python.py
# Name: Murphy Cheng
# JHED ID: 1800017781
###############################################################################

import sys
import socket
import threading

RECV_BUFFER_SIZE = 2048
QUEUE_LENGTH = 10

buffer_lock = threading.Lock()

def recv_data(conn):
    while True:
        data = conn.recv(RECV_BUFFER_SIZE)
        sys.stdout.write(data)
        sys.stdout.flush()
    conn.close()

def server(server_port):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', server_port))
    s.listen(QUEUE_LENGTH)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=recv_data, args=(conn,))
        t.start()
        conn.close()
        
    s.close()

def main():
    """Parse command-line argument and call server function """
    if len(sys.argv) != 2:
        sys.exit("Usage: python server-python.py [Server Port]")
    server_port = int(sys.argv[1])
    server(server_port)

if __name__ == "__main__":
    main()
