/*****************************************************************************
 * client-c.c
 * Name:
 * JHED ID:
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <netinet/in.h>
#include <errno.h>

#define SEND_BUFFER_SIZE 2048


int Socket(int domain, int type, int protocol) {
  int sock;
  if ((sock = socket(domain, type, protocol)) < 0)
  {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }
  return sock;
}

void Inet_pton(int domain, char *ip, struct in_addr *addr) {
  if (inet_pton(domain, ip, addr) <= 0) {
    perror("address failed");
    exit(EXIT_FAILURE);
  }
}

void Connect(int sock, struct sockaddr *addr, socklen_t addr_len) {
  if (connect(sock, addr, addr_len) < 0) {
    perror("connect failed");
    exit(EXIT_FAILURE);
  }
}

/* TODO: client()
 * Open socket and send message from stdin.
 * Return 0 on success, non-zero on failure
*/
int client(char *server_ip, char *server_port) {
  // create socket
  int sock = Socket(AF_INET, SOCK_STREAM, 0);
  
  // create server address
  struct sockaddr_in serv_addr;
  memset(&serv_addr, '0', sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(atoi(server_port));

  // convert IPv4 and IPv6 addresses from text to binary form
  Inet_pton(AF_INET, server_ip, &serv_addr.sin_addr);

  // connect to server
  Connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

  // send data
  char buffer[SEND_BUFFER_SIZE];
  fread(buffer, SEND_BUFFER_SIZE, 1, stdin);
  send(sock, buffer, strlen(buffer), 0);

  // close socket
  close(sock);

  return 0;
}

/*
 * main()
 * Parse command-line arguments and call client function
*/
int main(int argc, char **argv) {
  char *server_ip;
  char *server_port;

  if (argc != 3) {
    fprintf(stderr, "Usage: ./client-c [server IP] [server port] < [message]\n");
    exit(EXIT_FAILURE);
  }

  server_ip = argv[1];
  server_port = argv[2];
  return client(server_ip, server_port);
}
