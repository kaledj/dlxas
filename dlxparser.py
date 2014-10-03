'''
Deluxe Assembly Parser
======

Parses the input in two passes, returning the input transformed from assembly
to string representation of machine code. 
'''

import re
import instructions
from instructions import I_OPCODES, J_OPCODES, R_OPCODES, R_FUNCCODES, OPCODES
from directives import DIRECTIVES

SYMTAB = {}

def run(inputdata):
    instructionlist = firstpass(inputdata)
    # printsymtab(SYMTAB)
    # printsymtab(instructions.OPCODES)
    outputdata = secondpass(instructionlist)
    return outputdata

def firstpass(inputdata):
    ''' 
    The first pass calculates addresses for labels and stores instructions,
    rearranging them as specified by a directive. 
    ''' 
    instructionlist = []
    curraddr = 0
    for line in inputdata.splitlines():
        # print "Original line:", line
        partitioned = line.partition(';')[0].strip()
        # print "Partitioned line:", partitioned
        if not partitioned: 
            # Line was a comment
            continue 
        tokens = partitioned.split()
        token1 = tokens[0]
        if matchlabel(token1):
            SYMTAB[token1.strip(':')] = curraddr
            if len(tokens) == 1:
                token1 = 'nop'
                partitioned = partitioned + ' nop'
            else:
                token1 = tokens[1]
        if matchdirective(token1):
            directiveobj = directivehandler(partitioned, curraddr)
            curraddr = directiveobj.nextaddress()
            instructionlist.append(directiveobj)
        elif matchopcode(token1):
            instructionobj = opcodehandler(partitioned)
            curraddr = curraddr + 4
            instructionlist.append(instructionobj)
        else:
            raise Exception("Expected directive or opcode.")    
    return instructionlist

def secondpass(instructionlist):
    outputdata = []
    curraddr = 0
    for instruction in instructionlist:
        try:
            encoding = instruction.encode()
            if type(encoding) is str:
                address = "{0:08x}: ".format(curraddr)
                curraddr = curraddr + 4
                outputdata.append(address + encoding)
            elif type(encoding) is list:
                outputdata.extend(encoding)
            else:
                raise Exception("Encoding was neither str nor list of strings...")
        except AttributeError, e:
            print e

    return "\n".join(outputdata) 

def matchlabel(tomatch):
    if type(tomatch) != str:
        return False
    return tomatch[len(tomatch)-1] is ":"

def matchopcode(tomatch):
    if type(tomatch) != str:
        return False
    return tomatch in OPCODES

def matchdirective(tomatch):
    if type(tomatch) != str:
        return False
    if tomatch[0] is not ".":
        return False
    return tomatch in DIRECTIVES

def directivehandler(directiveline, curraddress):
    ''' 
    Coverts directive line to hex and computes data length. Returns the line
    transformed to line (or lines) of hex, and also the address of the next 
    instruction. 
    '''
    tokens = directiveline.split()
    directivetoken = tokens[0]
    argtokens = tokens[1:]
    if matchlabel(directivetoken):
        directivetoken = tokens[1]
        argtokens = tokens[2:]

    directiveclass = DIRECTIVES[directivetoken]
    directiveobj = directiveclass(curraddress, argtokens)
    return directiveobj

def compileregex():
    pass

def printsymtab():
    print "Symbol Table\n============"
    for key in SYMTAB:
        if type(SYMTAB[key]) is tuple:
            print "Symbol: '{0}' Value: {1}".format(key, SYMTAB[key])
        else:
            print "Symbol: '{0}' Value: {1:#x}".format(key, int(SYMTAB[key]))

def opcodehandler(instructionline):
    ''' Takes a line containing an instruction and returns the encoding. '''
    tokens = instructionline.split()
    opcodetoken = tokens[0]
    if matchlabel(opcodetoken):
        opcodetoken = tokens[1]
    if opcodetoken not in OPCODES:
        raise Exception(opcodetoken + " is not a valid opcode.")

    operandtokens = parseoperands(instructionline.split(opcodetoken, 1)[1])
    # print operandtokens
    opcode = OPCODES[opcodetoken]

    if opcodetoken in I_OPCODES:
        instrobj = instructions.IType(opcode, **operandtokens)
    if opcodetoken in J_OPCODES:
        instrobj = instructions.JType(opcode, **operandtokens)
    if opcodetoken in R_OPCODES:
        funccode = R_FUNCCODES[opcodetoken]
        if R_OPCODES[opcodetoken] == 0:
            instrobj = instructions.RALU(opcode, funccode, **operandtokens)
        else:     
            instrobj = instructions.RFPU(opcode, funccode, **operandtokens)
    return instrobj

def parseoperands(instructionline):
    re1 = re.compile(r'[rRfF](\d{1,2}), (\d+)\([rRfF](\d{1,2})\)')
    m1 = re1.search(instructionline)
    if m1:
        rdest, immediate, rs1 = m1.groups()
        return {'rdest':int(rdest), 'immediate': int(immediate), 'rs1': int(rs1)}

    re2 = re.compile(r'(\d+)\([rRfF](\d{1,2})\), [rRfF](\d{1,2})')
    m2 = re2.search(instructionline)
    if m2:
        immediate, rs1, rdest = m2.groups()
        return {'rdest':int(rdest), 'immediate': int(immediate), 'rs1':int(rs1)}

    re3 = re.compile(r'^[rRfF](\d{1,2}), [rRfF](\d{1,2})$')
    m3 = re3.search(instructionline)
    if m3:
        rdest, rs1 = m3.groups()
        return {'rdest':int(rdest), 'rs1':int(rs1)}

    re4 = re.compile(r'[rRfF](\d{1,2}), [rRfF](\d{1,2}), [rRfF](\d{1,2})')
    m4 = re4.search(instructionline)
    if m4:
        rdest, rs1, rs2 = m4.groups()
        return {'rdest':int(rdest), 'rs1':int(rs1), 'rs2':int(rs2)}

    re5 = re.compile(r'[rRfF](\d{1,2}), [rRfF](\d{1,2}), (\w+)')
    m5 = re5.search(instructionline)
    if m5:
        rdest, rs1, immediate = m5.groups()
        return {'rdest':int(rdest), 'rs1':int(rs1), 'immediate':immediate}
    
    re6 = re.compile(r'[rRfF](\d{1,2}), (\d+)')
    m6 = re6.search(instructionline)
    if m6:
        rdest, immediate = m6.groups()
        return {'rdest':int(rdest), 'immediate':int(immediate)}

    re7 = re.compile(r'(^(?![rRfF]\d{1,2})\w+)')
    m7 = re7.search(instructionline)
    if m7:
        name, = m7.groups()
        return {'name':name}

    re8 = re.compile(r'[rRfF](\d{1,2})')
    m8 = re8.search(instructionline)
    if m8:
        rs1, = m8.groups()
        return {'rs1':int(rs1)}

    re9 = re.compile(r'[rRfF](\d{1,2}), (^(?![rRfF]\d{1,2})\w+)')
    m9 = re9.search(instructionline)
    if m9:
        rs1, name = m9.groups()
        return {'rs1':int(rs1), 'name':name}

    return {}
