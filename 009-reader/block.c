#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>

static unsigned char *data = NULL;
static unsigned long long data_size = 0;

FILE *fin = NULL;

void setup(char *filename) {
  if (data)
    return;
  struct stat fileinfo;
  stat(filename, &fileinfo);
  data_size = fileinfo.st_size;

  data = (unsigned char *)malloc(0x2000);
  fin = fopen(filename, "rb");
}

void get(int blockno) {
  fseek(fin, 0x2000 * blockno, SEEK_SET);
  fread(data, 0x2000, 1, fin);
}

void teardown(void) {
  if (data) {
    free(data);
    data = NULL;
    data_size = 0;
    fclose(fin);
  }
}

int main(int argc, char **argv) {
  struct timespec t0, t1;

  clock_gettime(CLOCK_MONOTONIC, &t0);
  setup(argv[1]);
  int blocks = data_size / 0x2000;
  for (int j = 0; j < blocks; j++) {
    get(j);
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);

  double dt = ((double)t1.tv_sec + 1.0e-9 * t1.tv_nsec) -
              ((double)t0.tv_sec + 1.0e-9 * t0.tv_nsec);

  printf("%s %lld => %fms\n", argv[1], data_size, 1000.0 * dt);

  teardown();

  return 0;
}