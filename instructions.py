'''
Instructions.py
===============

This module:
1. Contains functions to load opcodes from files. This runs at module startup.
2. Implements instruction classes for the DLX assembler. 
3. Implements functions to create instructions dynamically at runtime
'''

import sys

I_OPCODES = {}
J_OPCODES = {}
R_OPCODES = {}
R_FUNCCODES = {}
OPCODES = {}
INSTRUCTIONS = {} 

def loadopcodes():
    ''' Loads opcodes from file into their respective mappings. '''
    try:
        with open('Itypes', 'r') as itypes:
            for line in itypes:
                split = line.split()
                I_OPCODES[split[0]] = int(split[1])
                OPCODES[split[0]] = int(split[1])
        with open('Jtypes', 'r') as jtypes:
            for line in jtypes:
                split = line.split()
                J_OPCODES[split[0]] = int(split[1])
                OPCODES[split[0]] = int(split[1])
        with open('Rtypes', 'r') as rtypes:
            for line in rtypes:
                split = line.split()
                R_OPCODES[split[0]] = int(split[1])
                R_FUNCCODES[split[0]] = int(split[2])
                OPCODES[split[0]] = int(split[1])
    except IOError, exc:
        sys.exit(str(exc))
loadopcodes()

class Instruction(object):
    ''' Base class for all Instruction subtypes. '''
    def __init__(self, opcode):
        self.opcode = opcode

    def nextaddress(self, curraddr):
        return curraddr + 4

class IType(Instruction):
    """ Base class for all I-Type instructions. """
    def __init__(self, opcode, rs1=0, rdest=0, immediate=0):
        super(IType, self).__init__(opcode)
        self.rs1 = rs1
        self.rdest = rdest
        self.immediate = immediate

    def getinfo(self):
        return "Type:I\nOpcode:%d\nRs1:%d\nRd:%d\nImmediate:%d" %(self.opcode, 
            self.rs1, self.rdest, self.immediate)

    def encode(self):
        from dlxparser import SYMTAB
        if type(self.immediate) is str:
            if self.immediate.isdigit():
                self.immediate = int(self.immediate)
            else:
                self.immediate = SYMTAB[self.immediate]
        instruction = self.opcode
        instruction = (instruction << 5) ^ self.rs1
        instruction = (instruction << 5) ^ self.rdest
        instruction = (instruction << 16) ^ (self.immediate & 0xffff)
        return "{0:08x}".format(instruction)

class Branch(IType):
    def __init__(self, opcode, rs1=0, rdest=0, immediate=0):
        super(IType, self).__init__(opcode)
        self.rs1 = rdest
        self.rdest = rs1
        self.immediate = immediate

    def encode(self, curraddr):
        from dlxparser import SYMTAB
        if type(self.immediate) is str:
            if self.immediate.isdigit():
                self.immediate = int(self.immediate)
            else:
                self.immediate = SYMTAB[self.immediate]
        relativeaddr = self.immediate - (curraddr + 4)
        instruction = self.opcode
        instruction = (instruction << 5) ^ self.rs1
        instruction = (instruction << 5) ^ self.rdest
        instruction = (instruction << 16) ^ (relativeaddr & 0xffff)
        return "{0:08x}".format(instruction)

class Trap(IType):
    def __init__(self, opcode, name=0):
        super(Trap, self).__init__(opcode)
        self.immediate = name    

class JType(Instruction):
    def __init__(self, opcode, name=0):
        super(JType, self).__init__(opcode)
        self.name = name

    def encode(self, curraddr):
        from dlxparser import SYMTAB
        if type(self.name) is str:
            if self.name.isdigit():
                self.name = int(self.name)
            else:
                self.name = SYMTAB[self.name]
        relativeaddr = self.name - (curraddr + 4)
        instruction = self.opcode
        instruction = (instruction << 26) ^ (relativeaddr & 0x3ffffff)
        return "{0:08x}".format(instruction)

class RType(Instruction):
    def __init__(self, opcode, func, rs1=0, rs2=0, rdest=0):
        super(RType, self).__init__(opcode)
        self.rs1 = rs1
        self.rs2 = rs2
        self.rdest = rdest
        self.func = func

class RALU(RType):
    def encode(self):
        ''' Returns the hex representation of the instruction as a string. '''
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rs2
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 5)
        instruction = (instruction << 6) + self.func
        return "{0:08x}".format(instruction)
    
class RFPU(RType):
    def encode(self):
        ''' Returns the hex representation of the instruction as a string. '''
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rs2
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 6)
        instruction = (instruction << 5) + self.func
        return "{0:08x}".format(instruction)

def needsPC(instructionojb):
    needs = [JType, Branch]
    if type(instructionojb) in needs:
        return True
    return False

def mapinstructions():
    ''' Performs the mapping to initialize INSTRUCTIONS. '''
    INSTRUCTIONS['beqz'] = Branch
    INSTRUCTIONS['bnez'] = Branch
    INSTRUCTIONS['trap'] = Trap
mapinstructions()
