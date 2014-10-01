'''
Instructions.py
===============

This module:
Contains functions to load opcodes from files. 
Maps directives to their respective class.
Implements instruction and directive classes for the DLX assembler. 
'''

import sys

I_OPCODES = {}
J_OPCODES = {}
R_OPCODES = {}

def loadopcodes():
    ''' Loads opcodes from file into their respective mappings. '''
    try:
        with open('Itypes', 'r') as itypes:
            for line in itypes:
                split = line.split()
                I_OPCODES[split[0]] = int(split[1])
        with open('Jtypes', 'r') as jtypes:
            for line in jtypes:
                split = line.split()
                J_OPCODES[split[0]] = int(split[1])
        with open('Rtypes', 'r') as rtypes:
            for line in rtypes:
                split = line.split()
                R_OPCODES[split[0]] = (int(split[1]), int(split[2]))
    except IOError, exc:
        sys.exit(str(exc))

class Instruction(object):
    ''' Base class for all Instruction subtypes. '''
    def __init__(self, opcode):
        self.opcode = opcode

    def encode(self):
        """ Returns the hex representation of the instruction as a string. """
        pass

class IType(Instruction):
    """ Base class for all I-Type instructions. """
    def __init__(self, opcode, rs1, rdest, immediate):
        super(IType, self).__init__(opcode)
        self.rs1 = rs1
        self.rdest = rdest
        self.immediate = immediate

    def getinfo(self):
        return "Type:I\nOpcode:%d\nRs1:%d\nRd:%d\nImmediate:%d" %(self.opcode, 
            self.rs1, self.rdest, self.immediate)

    def encode(self):
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 16) + self.immediate
        return "%08x" %(instruction)

class JType(Instruction):
    def __init__(self, opcode, name):
        super(IType, self).__init__(opcode)
        self.name = name

    def encode(self):
        instruction = self.opcode
        instruction = (instruction << 26) + self.name
        return hex(instruction)[2:]

class RType(Instruction):
    def __init__(self, opcode, rs1, rs2, rdest, func):
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
        return "%08x" %(instruction)
    
class RFPU(RType):
    def encode(self):
        ''' Returns the hex representation of the instruction as a string. '''
        instruction = self.opcode
        instruction = (instruction << 5) + self.rs1
        instruction = (instruction << 5) + self.rs2
        instruction = (instruction << 5) + self.rdest
        instruction = (instruction << 6)
        instruction = (instruction << 5) + self.func
        return "%08x" %(instruction)
 