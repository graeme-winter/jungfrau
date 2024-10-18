#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char **argv) {
  int sock, msg, total;
  struct sockaddr_in srv, src;
  char buf[8240];

  sock = socket(AF_INET, SOCK_DGRAM, 0);

  srv.sin_family = AF_INET;
  srv.sin_addr.s_addr = INADDR_ANY;
  srv.sin_port = ntohs(12345);

  bind(sock, (struct sockaddr *)&srv, sizeof(srv));

  total = 0;
  for (int i = 0; i < 100 * 2304; i++) {
    msg = recvfrom(sock, buf, sizeof(buf), 0, NULL, NULL);
    total += msg;
  }

  printf("Read %d bytes\n", total);

  close(sock);

  return 0;
}
