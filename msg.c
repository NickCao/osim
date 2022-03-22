#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/msg.h>

struct msgbuf {
  long mtype;
  char mtext[1];
};

int main(void) {
  // create a new anonymous message queue, with a permission of 0600
  // ref: https://man7.org/linux/man-pages/man2/msgget.2.html
  int msgid = msgget(IPC_PRIVATE, IPC_CREAT | 0600);
  if (msgid == -1) {
    perror("failed to create message queue");
    exit(EXIT_FAILURE);
  }

  int pid = fork();
  if (pid == -1) {
    perror("failed to fork");
    exit(EXIT_FAILURE);
  }

  if (pid == 0) {
    // child process receives message
    struct msgbuf buf;
    while (msgrcv(msgid, &buf, sizeof(buf.mtext), 1, 0) != -1) {
      printf("%c", buf.mtext[0]);
    }
  } else {
    // parent process sends message
    char* msg = "hello from message queue\n";
    struct msgbuf buf;
    buf.mtype = 1;
    for (int i = 0; i < strlen(msg); i ++) {
      buf.mtext[0] = msg[i];
      msgsnd(msgid, &buf, sizeof(buf.mtext), 0);
    }
    struct msqid_ds info;
    while (msgctl(msgid, IPC_STAT, &info), info.msg_qnum > 0) {
      // wait for the message queue to be fully consumed
    }
    // close message queue
    msgctl(msgid, IPC_RMID, NULL);
  }

  return EXIT_SUCCESS;
}
