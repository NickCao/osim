#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

int parse(char* line, char** argv) {
  size_t len;
  // read a line from stdin
  if (getline(&line, &len, stdin) == -1)
    return -1;
  // remove trailing newline
  line[strlen(line) - 1] = '\0';
  // split line into tokens
  int i = 0;
  char* token = strtok(line, " ");
  while (token != NULL) {
    argv[i] = token;
    token = strtok(NULL, " ");
    i++;
  }
  return 0;
}

int run(char** argv, int fdi, int fdo) {
  int pid = fork();
  if (pid == 0) {
    if (fdi != -1) {
      close(STDIN_FILENO);
      dup2(fdi, STDIN_FILENO);
    }
    if (fdo != -1) {
      close(STDOUT_FILENO);
      dup2(fdo, STDOUT_FILENO);
    }
    execvp(argv[0], argv);
  }
  return pid;
}

int concat(char** argv1, char** argv2) {
    // create pipe
    int pipefd[2];
    if (pipe(pipefd) == -1)
      return -1;

    // run the first command
    int pid1 = fork();
    if (pid1 == -1)
      return -1;
    if (pid1 == 0) {
      dup2(pipefd[1], STDOUT_FILENO);
      close(pipefd[0]);
      close(pipefd[1]);
      execvp(argv1[0], argv1);
    }

    // run the second command
    int pid2 = fork();
    if (pid2 == -1)
      return -1;
    if (pid2 == 0) {
      dup2(pipefd[0], STDIN_FILENO);
      close(pipefd[0]);
      close(pipefd[1]);
      execvp(argv2[0], argv2);
    }

    // wait for them to exit
    close(pipefd[0]);
    close(pipefd[1]);
    wait(&pid1);
    wait(&pid2);
    return 0;
}


int main(void) {
  printf("[command 1]$ ");
  char* line1 = NULL;
  char* argv1[16] = {NULL};
  if (parse(line1, argv1) == -1) {
    exit(EXIT_FAILURE);
  }
  printf("[command 2]$ ");
  char* line2 = NULL;
  char* argv2[16] = {NULL};
  if (parse(line2, argv2) == -1) {
    exit(EXIT_FAILURE);
  }
  concat(argv1, argv2);
  free(line1);
  free(line2);
}
