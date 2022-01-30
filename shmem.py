# shared memory is one of the most important IPC mechanisms
# it can be trivially implemented by mapping the same physical page
# into two or more processes' memory space
# however shared memory itself suffers from the limitation
# of varying memory orders across architectures
# and is thus mostly used together with other IPC means for
# proper synchronization
# however as we are most likely running this demo on x86
# which has total store ordering (stores on one core are
# observed on another core in the same order)
# we can simply use a flag bit to signal the completion of data store
from multiprocessing.managers import SharedMemoryManager
from multiprocessing import Process
from time import sleep

# sender waits a little bit of time before sending data
def sender(shm):
    # we send five numbers to the receiver
    for i in range(5):
        # pretend to be doing some compuation
        sleep(1)
        # wait for receiver to be ready
        while shm[0] != 0:
            pass
        print(f"sender: sending data: {i}")
        shm[1] = i
        # signal to receiver that data is ready
        shm[0] = 1

def receiver(shm):
    for i in range(5):
        # wait for data to be ready
        while shm[0] != 1:
            pass
        print(f"receiver: recevied data: {shm[1]}")
        # sigal to sender that receiver is ready
        shm[0] = 0

with SharedMemoryManager() as smm:
    shm = smm.ShareableList([0, 0])
    s = Process(target=sender, args=(shm,))
    r = Process(target=receiver, args=(shm,))
    s.start()
    r.start()
    s.join()
    r.join()
