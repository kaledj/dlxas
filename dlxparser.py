'''
Deluxe Assembly Parser
======

Parses the input in two passes, returning the input transformed from assembly
to string representation of machine code. 
'''

import instructions
from instructions import I_OPCODES, J_OPCODES, R_OPCODES
from directives import DIRECTIVES

def parse(inputdata):
    instructions.loadopcodes()
    findsymbols(inputdata)
    return "test\noutput"

def findsymbols(inputdata):
    ''' Parses input line by line, returning a complete symbol table. '''
    symtab = {}
    curraddr = 0
    for line in inputdata.splitlines():
        line = line.partition(';')[0].strip()
        
        # If label, store it with current address 
        # else if directive, modify address as needed
        # else opcode-> increment by 4 and proceed

    print directivehandler('.align', 16)
    print directivehandler('.align 1', 7)
    print directivehandler('.align 2', 9) 
    print directivehandler('.align 3', 15) 
    print directivehandler('.align 4', 1)     
    return symtab

def directivehandler(directiveline, address):
    ''' 
    Coverts directive line to hex and computes data length. Returns the line
    transformed to line (or lines) of hex, and also the address of the next 
    instruction. 
    '''
    linesplit = directiveline.split()
    directiveclass = DIRECTIVES[linesplit[0]]
    directiveobj = directiveclass(address, linesplit[1:])
    return directiveobj.nextaddress()
