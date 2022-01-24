# this is an illustrative simulation and interpretation of the RISC-V privileged architectures
# and is by no means close to real world implementations of the ISA
# for reference, see https://github.com/riscv/riscv-isa-manual/releases/download/Priv-v1.12/riscv-privileged-20211203.pdf 
from enum import Enum

from util import make_process

# RISC-V has four privilege levels, one of them is reserved
# as we are writing an operating system running at supervisor level
# we can pay less attention to machine level, as the interaction between
# supervisor and user, is mostly identical to the one between machine and supervisor
# while it may be hard for newcomers to grasp an idea of the role of each level
# knowing that every subsequent level is more privileged than the previous one is enough now
class PrivilegeLevel(Enum):
    User = 0
    Supervisor = 1
    Reserved = 2
    Machine = 3

# when a RISC-V machine boots, it starts in machine level
# and runs a special piece of software called Supervisor Binary Interface, SBI for short
# we normally call that "firmware" or something
# it then *switches privilege level* and handles control
# to our operating system running in supervisor level
# whose job is to *switch privilege level* again and handle control 
# to the userland programs

# but why should privilege levels exist in the first place
# if their only purpose is to pass the control to lower levels
# the answer is obvious, imagine a machine with two users
# one of them is badly behaved, he not only wants to steal
# the other one's secrets, but also run a deadloop forever
# so that nobody can use the machine other than him
# this is exactly when we need a supervisor
# who regulate the behavior of lower levels

# specifically, we need a mechanism to transfer control
# back to higher privilege levels, when an *exception* or an *interrupt* fires
# speaking of exceptions, a prominent example is illegal instruction
# programs running in low privilege levels may try to run privileged instructions
# which is certainly something the supervisor should be notified of
# for interrupts, timer interrupt is the most common one
# so that the supervisor can check from time to time
# whether someone is taking the machine for too long
# the mechanism in question, is called trap

# for controlling the interaction between privilege levels
# such as what to do when a trap occurs
# RISC-V has special registers called: Control and Status Register, CSR for short
# there are hundreds of CSRs in the current RISC-V specification
# thus we would only focus on a few interesting ones

# stvec: supervisor trap vector base address register
# controls where should the machine jump to on traps
class STVec():
    class Mode(Enum):
        Direct = 0 # just set pc to BASE
        Vectored = 1 # set pc to BASE+4×cause
    base = 0 # a valid memory address
    mode = Mode.Direct # how to calculate the target address relative to BASE

# scause: supervisor cause register
# tells the supervisor cause of the trap
class SCause():
    interrupt = False # whether the trap is cause by an interrupt or an exception
    code = 0 # type of the interrupt or exception, for example exception number 2 is illegal instruction

# sepc: supervisor exception program counter
class SEPC():
    # address of the instruction that was interrupted or caused the exception
    # also the address to return to after we handled the trap
    sepc = 0 

# sstatus: supervisor status register
# this is a particularly heavy duty CSR packed with many fields
# and we intentionally omit most of them for easier understanding
class SStatus():
    # the privilege level the machine was at before the trap
    # also the privilege level to enter after we return from the trap
    spp = PrivilegeLevel.User

# now we are ready to assemble our RISC-V machine
class Machine():
    general = [0] * 32 # general purpose registers
    stvec = STVec() 
    scause = SCause()
    sepc = SEPC()
    sstatus = SStatus()
    priv = PrivilegeLevel.Supervisor
    def sret(self):
        # switch privilege level to spp
        self.priv = self.sstatus.spp
        print(f"machine: we are now at {self.priv} level")
        # jump to sepc
        self.sepc.sepc()
    def ecall(self, next):
        self.scause.interrupt = False
        self.sstatus.spp = self.priv 
        self.sepc.sepc = next # should be set to the instruction after ecall
        if self.priv == PrivilegeLevel.User:
            self.scause.code = 8 # environment call from user level
            self.priv = PrivilegeLevel.Supervisor
            print(f"machine: we are now at {self.priv} level")
            if self.stvec.mode == STVec.Mode.Direct:
                self.stvec.base()
            elif self.stvec.mode == STVec.Mode.Vectored:
                # calculate the offset then jump
                pass
        # the handling for ecall called in supervisor level, not used in our demo though
        elif self.priv == PrivilegeLevel.Supervisor:
            self.scause.code = 9 # environment call from supervisor level
            self.priv = PrivilegeLevel.Machine
            # and ......
    # and simulate the execution of the machine
    # (imagine if the code below are just RISC-V assembly)
    def run(self):
        def trap_handler():
            if self.scause.interrupt:
                # handle interrupts
                pass
            else:
                if self.scause.code == 8:
                    # handle ecall from user level
                    if self.general[17] == 1:
                        # handle print
                        print(f"print: {self.general[10]}")
                    else:
                        # handle other syscalls
                        pass
                else:
                    # handler the rest of exceptions
                    pass
            # after handling the trap
            # use sret to continue the execution of user program
            self.sret()

        @make_process
        def user_program():
            # print("hello from user level")
            # wait, can we just do that here
            # were we printing to a serial console
            # we may not want to implement a uart driver
            # in every userland application
            # instead we transfer control to the operating system
            # so that it can do the printing for us
            # and we call this, a syscall
            self.general[10] = "hello from user" # put syscall argument in a0-a5 (should be a pointer to string)
            self.general[17] = 1 # put syscall number in a7, let's just use 1 for print
            print("debug: calling ecall from user level to print string")
            yield self.ecall
            print("debug: back at user level after ecall")
        # when initializing our operation system
        # we should first set stvec to the address
        # of our trap handler, for simplicity in implementation
        # we use the direct mode
        self.stvec.mode = STVec.Mode.Direct
        self.stvec.base = trap_handler
        # we are now ready to enter user level, but how
        # reading the ISA specification
        # you would find that the only instruction that seems appropriate
        # is sret
        # remeber spp field from sstatus and sepc
        # they not only provides us with information about the trap
        # they also tells the machine what to do after the trap
        self.sepc.sepc = user_program
        self.sstatus.spp = PrivilegeLevel.User
        print("debug: calling sret from supervisor level to enter user program")
        self.sret()

machine = Machine()
machine.run()
