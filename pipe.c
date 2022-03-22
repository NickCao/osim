#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
  int pipefd[2];
  // pipe syscall creates a pipe with two ends
  // pipefd[0] is the read end
  // pipefd[1] is the write end
  // ref: https://man7.org/linux/man-pages/man2/pipe.2.html
  if (pipe(pipefd) == -1) {
    perror("failed to create pipe");
    exit(EXIT_FAILURE);
  }

  int pid = fork();
  if (pid == -1) {
    perror("failed to fork");
    exit(EXIT_FAILURE);
  }

  if (pid == 0) {
    // child process reads from the pipe
    close(pipefd[1]); // close the write end
    // read a byte at a time
    char buf;
    while (read(pipefd[0], &buf, 1) > 0) {
      printf("%s", &buf);
    }
    close(pipefd[0]); // close the read end
  } else {
    // parent process writes to the pipe
    close(pipefd[0]); // close the read end
    // parent writes
    char* msg = "hello from pipe\n";
    write(pipefd[1], msg, strlen(msg)); // omitting error handling
    close(pipefd[1]); // close the write end
  }

  return EXIT_SUCCESS;
}
