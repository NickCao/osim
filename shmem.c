#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/shm.h>

int main(void) {
  // create a new anonymous shared memory segment of page size, with a permission of 0600
  // ref: https://man7.org/linux/man-pages/man2/shmget.2.html
  int shmid = shmget(IPC_PRIVATE, sysconf(_SC_PAGESIZE), IPC_CREAT | 0600);
  if (shmid == -1) {
    perror("failed to create shared memory");
    exit(EXIT_FAILURE);
  }

  int pid = fork();
  if (pid == -1) {
    perror("failed to fork");
    exit(EXIT_FAILURE);
  }

  if (pid == 0) {
    // attach the shared memory into child process's address space
    char* shm = shmat(shmid, NULL, 0);
    while (!shm[0]) {
      // wait until the parent signals that the data is ready
      // WARNING: this is not the correct way to synchronize processes
      // on SMP systems due to memory orders, but this implementation
      // is choosen here specifically for ease of understanding
    }
    printf("%s", shm + 1);
  } else {
    // attach the shared memory into parent process's address space
    char* shm = shmat(shmid, NULL, 0);
    // copy message into shared memory
    strcpy(shm + 1, "hello from shared memory\n");
    // signal that the data is ready
    shm[0] = 1;
  }

  return EXIT_SUCCESS;
}
