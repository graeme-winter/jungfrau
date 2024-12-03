#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char **argv) {
  int microseconds = 500, ticks = 0;

  if (argc == 1) {
    fprintf(stderr, "%s ticks\n", argv[0]);
    return 1;
  }

  ticks = atoi(argv[1]);

  struct timespec t0, tn;

  clock_gettime(CLOCK_MONOTONIC, &t0);

  for (int j = 0; j < ticks; j++) {
    double target = j * (double)microseconds * 1.0e-6;
    while (1) {
      clock_gettime(CLOCK_MONOTONIC, &tn);
      double dt = ((double)tn.tv_sec + 1.0e-9 * tn.tv_nsec) -
                  ((double)t0.tv_sec + 1.0e-9 * t0.tv_nsec);
      if (dt > target) {
        printf("%d %f\n", j, dt);
        break;
      }
    }
  }

  return 0;
}