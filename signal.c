#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

static void sighandler(int sig) {
  printf("received signal %d, exiting\n", sig);
  exit(EXIT_SUCCESS);
}

int main(void) {
  struct sigaction sa;
  sa.sa_handler = sighandler;
  sa.sa_flags = 0;
  sigemptyset(&sa.sa_mask);
  // register function sighandler as signal handler for SIGUSR1
  if (sigaction(SIGUSR1, &sa, NULL) != 0) {
    perror("failed to register signal handler");
    exit(EXIT_FAILURE);
  }

  int pid = fork();
  if (pid == -1) {
    perror("failed to fork");
    exit(EXIT_FAILURE);
  }

  if (pid == 0) {
    while (1) {
      // loop and wait for signal
    }
  } else {
    // send SIGUSR1 to child process
    kill(pid, SIGUSR1);
  }

  return EXIT_SUCCESS;
}
