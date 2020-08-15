"""CPU functionality."""

import sys

# PC: Program Counter, address of the currently executing instruction
# IR: Instruction Register, contains a copy of the currently executing instruction
# MAR: Memory Address Register, holds the memory address we're reading or writing
# MDR: Memory Data Register, holds the value to write or the value just read
# FL: Flags

LDI     =   0b10000010
PRN     =   0b01000111
HLT     =   0b00000001
MUL     =   0b10100010 
PUSH    =   0b01000101
POP     =   0b01000110
CALL    =   0b01010000
RET     =   0b00010001
ADD     =   0b10100000

#  Our dev algotrithm for adding commands
##  add code to top
##  add code and function to branchtable
##  add function

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256    # 256 bytes of RAM (memory)
        self.reg = [0] * 8      # 8 registers ==> R0 through R7
        self.pc = 0             # program counter
        self.reg[7] = 0xF4      # stack pointer for push & pop operations
        self.running = True

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret



    # def load(self):
        """Load a program into memory."""
        # # For now, we've just hardcoded a program:
        # address = 0

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8 (load a number into a register)
        #     0b00000000,  # R0
        #     0b00001000,  # 8 (value to print)
        #     0b01000111,  # PRN R0
        #     0b00000000,  # Register 0
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

#------------------------------------------------------------------------------
# # Unhardcode the Machine Code

    def load(self, filename):
        address = 0
        # print(address)
        try:
            with open(filename) as file:
                for line in file:
                    # print(line)
                    comment_split = line.split('#')
                    possible_num = comment_split[0]

                    if possible_num == '':
                        continue

                    if possible_num[0] == '1' or possible_num[0] == '0':
                        num = possible_num[:8]
                        # print(f'{num}: {int(num, 2)}')

                        self.ram[address] = int(num, 2)
                        address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}:{sys.argv[1]} not found')     
        
    def ram_read(self, MAR):
        """
        accepts address to read
        returns value stored there
        """
        return self.ram[MAR]
    
    def ram_write(self, MDR, MAR):
        """
        acccepts value to write and adress to write it to
        writes value to memory at that address
        """
        self.ram[MAR] = MDR

    def alu(self, op, operand_a, operand_b):
        """ALU operations."""

        if op == ADD:
            self.reg[operand_a] += self.reg[operand_b]
        elif op == MUL:
                self.reg[operand_a] *= self.reg[operand_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
       
        while self.running:

         #  get command
            IR= self.ram[self.pc]   # command; where pc is
            # we might not use these, depending on the command.  Get them just in case
            operand_a = self.ram_read(self.pc + 1)
            # print(operand_a)
            operand_b = self.ram_read(self.pc + 2)
            # print(operand_b)

         # update program counter
         # look at the first two bits of the instruction

            sets_pc_directly = IR>>4 & 0b0001
            if not sets_pc_directly:
                self.pc += 1 + (IR>>6)

        #  if IR is an ALU command, send to ALU

            is_alu_command = IR & 0b00100000            #  classmate's way: check the 3rd bit
            # is_alu_command = ((IR>>5) & 0b001) == 1   #  Tim's way: delete last 5 & check the 3rd bit

            if is_alu_command:
                self.alu(IR, operand_a, operand_b)
            else:
                self.branchtable[IR](operand_a, operand_b)

    def hlt(self,*_):       #  ==>  " *_ " represents all the unused arguments
        self.running = False

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, *_):
        print(self.reg[operand_a])
    
    def push(self, operand_a, *_):
        #  decrement SP in R7
        self.reg[7] -= 1
        #  Assign variable 
        sp = self.reg[7]
        # first operand is address of register holding value
        value = self.reg[operand_a]
        # put that value in memory
        self.ram[sp] = value  
        # shortened version:
        # #  self.ram[sp] = self.reg[operand_a] 

    def pop (self, operand_a, *_):
        # get value of ram[SP]
        sp = self.reg[7]
        value = self.ram[sp]
        # write to reg[operand_a]
        self.reg[operand_a] = value
        # increment SP
        self.reg[7] += 1
    
    def call(self, operand_a, *_):
        # decrement the SP
        self.reg[7] -= 1
        sp = self.reg[7]
        # get address for RET
        return_address = self.pc + 2
        # put that value in memory
        self.ram[sp] = return_address 

        destination_address = self.reg[operand_a]
        self.pc = destination_address

    def ret(self, *_):
        # pop from stack
        sp = self.reg[7]
        value = self.ram[sp]
        # set PC to value popped from stack
        self.pc = value
        # increment SP
        self.reg[7] += 1



