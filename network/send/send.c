#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>

int main(int argc, char **argv) {
  int sock;
  struct sockaddr_in dest;
  uint16_t data[24 + 4096];
  struct timespec t0, t1;
  double dt;
  char *tmp;

  /* horrible parsing of an IP address on the command line */

  uint32_t addr;
  uint8_t *_addr = (uint8_t *)&addr;
  tmp = strtok(argv[1], ".");
  for (int j = 0; j < 4; j++) {
    _addr[j] = atoi(tmp);
    tmp = strtok(NULL, ".");
  }

  sock = socket(AF_INET, SOCK_DGRAM, 0);

  dest.sin_family = AF_INET;
  dest.sin_port = htons(12345);
  dest.sin_addr.s_addr = addr;

  clock_gettime(CLOCK_MONOTONIC, &t0);

  for (int i = 0; i < 100 * 2304; i++) {
    sendto(sock, data, 2 * (24 + 4096), 0, (struct sockaddr *)&dest,
           sizeof(dest));
  }

  clock_gettime(CLOCK_MONOTONIC, &t1);

  dt = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
  printf("sending %d bytes took %.3fs\n", 8240 * 100 * 2304, dt);
  printf(" => %.3f Gb/s\n", 15.187968 / dt);

  return 0;
}
