# Do not communicate by sharing memory; instead, share memory by communicating. - Effective Go
# inter process communication by sharing memory is likely to cause race conditions
# pipe, works around that deficiency by providing an interface that you cannot misuse
# just like a water pipe, pipe connects two processes, creating a channel
# in which messages can flow
from multiprocessing import Process, Pipe
from time import sleep

# sender waits a little bit of time before sending data
def sender(tx):
    # we send five numbers to the receiver
    for i in range(5):
        # pretend to be doing some compuation
        sleep(1)
        print(f"sender: sending data: {i}")
        tx.send(i)

def receiver(rx):
    for i in range(5):
        # recv blocks if there is no data to read
        data = rx.recv()
        print(f"receiver: recevied data: {data}")

tx, rx = Pipe()
s = Process(target=sender, args=(tx,))
r = Process(target=receiver, args=(rx,))
s.start()
r.start()
s.join()
r.join()
