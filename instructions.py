"""
Instructions 
============

This module:
1) Provides types for all DLX instructions. Instructions are responsible for 
        knowing to encode themselves.
2) Contains constants for mappings for opcode to mnemonic. 
3) Contains a constant mapping for certain opcode mnemonics to their respective
        types. Some special cases are required when instruction keyword 
        parameters are named differently.
4) At startup time, reads opcode mnemonics from file. 
"""

import sys

I_OPCODES = {}
J_OPCODES = {}
R_OPCODES = {}
R_FUNCCODES = {}
OPCODES = {}
INSTRUCTIONS = {} 

def loadopcodes():
    """ Loads opcodes from file into their respective mappings. """
    try:
        with open("Itypes", "r") as itypes:
            for line in itypes:
                split = line.split()
                I_OPCODES[split[0]] = int(split[1])
                OPCODES[split[0]] = int(split[1])
        with open("Jtypes", "r") as jtypes:
            for line in jtypes:
                split = line.split()
                J_OPCODES[split[0]] = int(split[1])
                OPCODES[split[0]] = int(split[1])
        with open("Rtypes", "r") as rtypes:
            for line in rtypes:
                split = line.split()
                R_OPCODES[split[0]] = int(split[1])
                R_FUNCCODES[split[0]] = int(split[2])
                OPCODES[split[0]] = int(split[1])
    except IOError, exc:
        sys.exit(str(exc))
loadopcodes()

class Instruction(object):
    """ 
    Base class for all Instruction subtypes. 

    Provides common initialization functionality. Also provides common
    functionality for incrementing the address during assembly. 
    """

    def __init__(self, opcode):
        self.opcode = opcode

    def nextaddress(self, curraddr):
        """ Returns the incremented memory address. """
        return curraddr + 4

class IType(Instruction):
    """ 
    Base class for all I-type instructions. 

    Provides the common initialization for I-type instructions, which is to 
    take an opcode, source register, destination register, and immediate value.
    All parameters have default values of 0. 
    I-types mostly use immediate addressing, so base encoding for those that do
    is provided. 
    """

    def __init__(self, opcode, rs1=0, rdest=0, immediate=0):
        super(IType, self).__init__(opcode)
        self.rs1 = rs1
        self.rdest = rdest
        self.immediate = immediate

    def encode(self):
        """
        Encodes an I-type instruction. 
        
        Builds an instruction from instance variables, and returns it in a hex
        representation. If the immediate value is a label, it's value is 
        retrieved from the symbol table. 
        """
        if type(self.immediate) is str:
            if self.immediate.isdigit():
                self.immediate = int(self.immediate)
            else:
                from dlxparser import SYMTAB
                self.immediate = SYMTAB[self.immediate]
        instruction = self.opcode
        instruction = (instruction << 5) ^ self.rs1
        instruction = (instruction << 5) ^ self.rdest
        instruction = (instruction << 16) ^ (self.immediate & 0xffff)
        return "{0:08x}".format(instruction)

class Branch(IType):
    """
    Implements a more specific I-type instruction: Branch

    Branch implements encoding as PC relative, so current address must be given
    so that the correct offset can be calculated. 
    """

    def __init__(self, opcode, rs1=0, rdest=0, immediate=0):
        super(IType, self).__init__(opcode)
        self.rs1 = rdest
        self.rdest = rs1
        self.immediate = immediate

    def encode(self, curraddr):
        """ 
        Encodes the branch instruction. 

        Branch instruction is encoded relative to the current address. If the 
        branch target is a label, it's value is retrieved from the symbol table.
        Otherwise an immediate value is used.
        """
        if type(self.immediate) is str:
            if self.immediate.isdigit():
                self.immediate = int(self.immediate)
            else:
                from dlxparser import SYMTAB
                self.immediate = SYMTAB[self.immediate]
        relativeaddr = self.immediate - (curraddr + 4)
        instruction = self.opcode
        instruction = (instruction << 5) ^ self.rs1
        instruction = (instruction << 5) ^ self.rdest
        instruction = (instruction << 16) ^ (relativeaddr & 0xffff)
        return "{0:08x}".format(instruction)

class Trap(IType):
    """
    Implements a more specific I-type instruction: Trap

    The difference is that trap is required to have a 'name' keyword, to
    simply parsing. 
    """

    def __init__(self, opcode, name=0):
        super(Trap, self).__init__(opcode)
        self.immediate = name    

class JType(Instruction):
    """ 
    Base class for all J-type instructions. 

    Provides the common initialization for J-type instructions, which is to 
    take an opcode and name. Jumps are done relative to the PC, so the current
    address must be passed in for encoding.    
    """

    def __init__(self, opcode, name=0):
        super(JType, self).__init__(opcode)
        self.name = name

    def encode(self, curraddr):
        """ 
        Encodes the jump instruction. 

        Jump instruction is encoded relative to the current address. If the 
        jump target is a label, it's value is retrieved from the symbol table.
        Otherwise an immediate value is used.
        """
        if type(self.name) is str:
            if self.name.isdigit():
                self.name = int(self.name)
            else:
                from dlxparser import SYMTAB
                self.name = SYMTAB[self.name]
        relativeaddr = self.name - (curraddr + 4)
        instruction = self.opcode
        instruction = (instruction << 26) ^ (relativeaddr & 0x3ffffff)
        return "{0:08x}".format(instruction)

class RType(Instruction):
    """ 
    Base class for all R-type instructions. 

    Provides the common initialization for R-type instructions, which is to 
    take an opcode, function code, two source registers, and a destination 
    register.    
    """

    def __init__(self, opcode, func, rs1=0, rs2=0, rdest=0):
        super(RType, self).__init__(opcode)
        self.rs1 = rs1
        self.rs2 = rs2
        self.rdest = rdest
        self.func = func

class RALU(RType):
    """ 
    A more specific R-type instruction class. 

    Provides the specific encoding functionality required by R-ALU instructions.
    """

    def encode(self):
        """ Returns the hex representation of the instruction as a string. """
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rs2
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 5)
        instruction = (instruction << 6) + self.func
        return "{0:08x}".format(instruction)
    
class RFPU(RType):
    """ 
    A more specific R-type instruction class. 

    Provides the specific encoding functionality required by R-FLU instructions.
    """

    def encode(self):
        """ Returns the hex representation of the instruction as a string. """
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rs2
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 6)
        instruction = (instruction << 5) + self.func
        return "{0:08x}".format(instruction)

def needsPC(instructionojb):
    """ Returns whether a given instruction requires PC to be encoded. """
    needs = [JType, Branch]
    if type(instructionojb) in needs:
        return True
    return False

def mapinstructions():
    """ Performs the mapping to initialize INSTRUCTIONS. """
    INSTRUCTIONS["beqz"] = Branch
    INSTRUCTIONS["bnez"] = Branch
    INSTRUCTIONS["trap"] = Trap
mapinstructions()
