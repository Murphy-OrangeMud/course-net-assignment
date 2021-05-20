/*****************************************************************************
 * server-c.c
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

#define QUEUE_LENGTH 10
#define RECV_BUFFER_SIZE 2048

int Socket(int domain, int type, int protocol) {
  int server_fd = socket(domain, type, protocol);
  if (server_fd == 0) {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }
}

void Setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen) {
  if (setsockopt(sockfd, level, optname, optval, optlen))
  {
    perror("setsockopt failed");
    exit(EXIT_FAILURE);
  }
}

void Bind(int fd, struct sockaddr *addr, socklen_t addr_len) {
  if (bind(fd, addr, addr_len) < 0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }
}

void Listen(int fd, int n) {
  if (listen(fd, n) < 0)
  {
    perror("listen failed");
    exit(EXIT_FAILURE);
  }
}

int Accept(int fd, struct sockaddr *addr, socklen_t *addr_len) {
  int sock = accept(fd, addr, addr_len);
  if (sock < 0)
  {
    perror("accept failed");
    exit(EXIT_FAILURE);
  }
  return sock;
}

int Fork() {
  int pid = fork();
  if (pid < 0) {
    perror("fork failed");
    exit(EXIT_FAILURE);
  }
  return pid;
}

/* TODO: server()
 * Open socket and wait for client to connect
 * Print received message to stdout
 * Return 0 on success, non-zero on failure
*/
int server(char *server_port) {
  // create socket file descriptor
  int server_fd = Socket(AF_INET, SOCK_STREAM, 0);

  // create socket address
  // forcefully attach socket to the port
  struct sockaddr_in address;
  int opt = 1;

  Setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));
  
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(atoi(server_port));

  // bind socket to address
  Bind(server_fd, (struct sockaddr *)&address, sizeof(address));

  // listen to incoming connections
  Listen(server_fd, 1024);

  int pid;
  while (1) {
    int addrlen = sizeof(address);
    int sock = Accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
    if ((pid = Fork()) == 0) {
      // child process
      // accept a connection
      close(server_fd);

      // receive message
      char buffer[RECV_BUFFER_SIZE];
      int recv_bytes = recv(sock, buffer, RECV_BUFFER_SIZE, 0);
      fwrite(buffer, recv_bytes, 1, stdout);
      fflush(stdout);

      // close socket
      close(sock);
    }
    close(sock);
  }

  return 0;
}

/*
 * main():
 * Parse command-line arguments and call server function
*/
int main(int argc, char **argv) {
  char *server_port;

  if (argc != 2) {
    fprintf(stderr, "Usage: ./server-c [server port]\n");
    exit(EXIT_FAILURE);
  }

  server_port = argv[1];
  return server(server_port);
}
