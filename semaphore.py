# semaphore, despite the nice looking name, is just atomic integer under the hood
# on modern CPU, semaphores are implemented with specialized instructions
# for example, A extension on RISC-V (https://five-embeddev.com/riscv-isa-manual/latest/a.html)
# imaging youself as a waiter in a restaurant with three seats
# your job is to make sure that there are at most three customers inside the restaurant
# or otherwise some customers will have no where to sit
# were you the only waiter, the solution would be as simple as taking a note
# of the number of empty seats currently inside the restaurant
# when someone enters, decrease that counter by one
# when someone leave, increase by one
# when the counter reaches zero, politely ask the next customer to wait a while
# however if there are more than one waiter, the situation is worsen
# (just like on a computer system with multiple processes running simultaneously)
# let's say that the two waiters are named A and B
# then the following sequence of events happened one day
# A: checks the counter, and it reads 1
# A: let the next customer go inside
# B: checks the counter, and it reads 1
# B: let the next customer go inside
# A: writes 0 to the counter
# B: writes 0 to the counter
# Oops, there are now four customers in the restaurant
# the reason behind this disastrous scenario is that
# decreasing the counter by one is not a single, atomic action
# it is composed by two actions
# tmp = counter
# counter = tmp - 1
# in between the two actions, another process may have written to the same counter
# by using semaphore, the race condition can be mitigated elegantly
# and more importantly, efficently without incurring the cost of a lock
from multiprocessing.managers import SharedMemoryManager
from multiprocessing import Process, Semaphore
from time import sleep

def decrease_by_three(n, shm, sem):
    for _ in range(3):
        print(f"process {n} decreasing counter by one")
        if sem:
            sem.acquire()
        tmp = shm[0]
        # sleeping to make the race condition more likely to be reached
        sleep(1)
        shm[0] = tmp - 1
        if sem:
            sem.release()

print("running multi processes without using semaphore for sync")
with SharedMemoryManager() as smm:
    shm = smm.ShareableList([9])
    print(f"counter is {shm[0]}")
    processes = []
    for n in range(3):
        p = Process(target=decrease_by_three, args=(n, shm, None))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    print(f"counter is {shm[0]}")
print("and we are getting wrong computation result")

print("running multi processes with semaphore for sync")
with SharedMemoryManager() as smm:
    sem = Semaphore(1)
    shm = smm.ShareableList([9])
    print(f"counter is {shm[0]}")
    processes = []
    for n in range(3):
        p = Process(target=decrease_by_three, args=(n, shm, sem))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    print(f"counter is {shm[0]}")
print("the critical section is properly protected, and the result is correct")
