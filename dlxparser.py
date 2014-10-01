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
    symtab = findsymbols(inputdata)
    printsymtab(symtab)
    outputdata = assemble(inputdata, symtab)
    return outputdata

def findsymbols(inputdata):
    ''' Parses input line by line, returning a complete symbol table. '''
    symtab = {}
    curraddr = 0
    for line in inputdata.splitlines():
        print "Original line:", line
        partitioned = line.partition(';')[0].strip()
        print "Partitioned line:", partitioned
        if not partitioned: 
            continue # Line was a comment
        tokens = partitioned.split()

        token1 = tokens[0]
        if matchlabel(token1):
            symtab[token1] = curraddr
            token1 = tokens[1]
        if matchdirective(token1):
            curraddr = directivehandler(line, curraddr)
        elif matchopcode(token1):
            curraddr = curraddr + 4
        else:
            raise RuntimeError("Expected directive or opcode.")    
    return symtab

def assemble(inputdata, symtab):
    ''' Assembles the input data using a given symbol table. '''
    return "MACHINE CODE" 

def matchlabel(tomatch):
    if type(tomatch) != str:
        return False
    if tomatch[len(tomatch)-1] is ":":
        return True
    return False

def matchopcode(tomatch):
    if type(tomatch) != str:
        return False
    isini = tomatch in I_OPCODES
    isinj = tomatch in J_OPCODES
    isinr = tomatch in R_OPCODES
    if isini or isinj or isinr:
        return True
    return False

def matchdirective(tomatch):
    if type(tomatch) != str:
        return False
    if tomatch[0] is not ".":
        return False
    if tomatch in DIRECTIVES:
        return True
    return False

def directivehandler(directiveline, curraddress):
    ''' 
    Coverts directive line to hex and computes data length. Returns the line
    transformed to line (or lines) of hex, and also the address of the next 
    instruction. 
    '''
    linesplit = directiveline.split()
    directiveclass = DIRECTIVES[linesplit[0]]
    directiveobj = directiveclass(curraddress, linesplit[1:])
    return directiveobj.nextaddress()

def compileregex():
    pass

def printsymtab(symtab):
    print "Symbol Table\n============"
    for key in symtab:
        print "Symbol: '{0}' Value: {1:#x}".format(key, int(symtab[key]))
