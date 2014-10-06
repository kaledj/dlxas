"""
Deluxe Assembly Parser
======================

This module takes as input a DLX assembly program (in a string) and returns 
the assembled program. Assembly is done in two passes: 
    1) First, the input is parsed for symbols. When a symbol is found it is stored 
    in the module global symbol table. Also, each line is parsed to determine 
    what it contained, i.e. an optional label, then either an operation 
    instruction or a directive. These are converted to objects and stored in 
    order. 
    2) The instruction objects are processed one by one, their encodings 
    corresponding to one or more lines of machine code output. 
This module contains functionality for determining which type of instruction
should be created for a given line. Operand values are parsed from a line using
regualar expressions. For example:
        
        addi r1, r2, 8 --> {'rd': 1, 'rs1': 2, 'immediate': 8}
"""

import re, instructions
from instructions import I_OPCODES, J_OPCODES, R_OPCODES, R_FUNCCODES 
from instructions import OPCODES, INSTRUCTIONS
from directives import DIRECTIVES

SYMTAB = {}

def run(inputdata):
    instructionlist = firstpass(inputdata)
    outputdata = secondpass(instructionlist)
    return outputdata

def firstpass(inputdata):
    """ 
    The first pass of the assembler. 

    At this step, calculates addresses for labels and stores instructions,
    rearranging them as specified by a directive. 
    
    Algorithmically:
        
        for each line of input
            remove comments and blank lines
            split line into tokens
            if first token is a label
                store label
                insert nop if label was on an empty line
            if first token excluding label is an directive
                create appropriate directive object by parsing tokens
                increment address based on directive
            if first token excluding label is an opcode
                create appropriate instruction object by parsing tokens
                increment address based on instruction length
            add object to list of processed lines
        return processed lines
    """ 

    instructionlist = []
    curraddr = 0
    for line in inputdata.splitlines():
        partitioned = line.partition(";")[0].strip()
        if not partitioned: # Line was a comment
            continue 
        tokens = partitioned.split()
        token1 = tokens[0]
        if matchlabel(token1):
            SYMTAB[token1.strip(":")] = curraddr
            if len(tokens) == 1:
                token1 = "nop"
                partitioned = partitioned + " nop"
            else:
                token1 = tokens[1]
        if matchdirective(token1):
            directiveobj = directivehandler(partitioned)
            curraddr = directiveobj.nextaddress(curraddr)
            instructionlist.append(directiveobj)
        elif matchopcode(token1):
            instructionobj = opcodehandler(partitioned)
            curraddr = curraddr + 4
            instructionlist.append(instructionobj)
        else:
            raise Exception("Expected directive or opcode.")    
    return instructionlist

def secondpass(instructionlist):
    """ 
    The second pass of the assembler. 

    At this step, generate encodings for every object returned by the first pass. 

    Algorithmically:
        
        for each line-object
            encode object
            concatenate encoding with current address
            increment address based on object
            add fully encoded line or lines to output
        return output
    """ 

    outputdata = []
    curraddr = 0
    for instruction in instructionlist:
        if instructions.needsPC(instruction):
            encoding = instruction.encode(curraddr)
        else:
            encoding = instruction.encode()
        if encoding:
            if type(encoding) is str: # Object required one line
                address = "{0:08x}: ".format(curraddr)
                outputdata.append(address + encoding)
            elif type(encoding) is list: # Object requires multiple lines
                addresses = instruction.nextaddresses(curraddr)
                for addr, enc in zip(addresses, encoding):
                    address = "{0:08x}: ".format(addr)
                    outputdata.append(address + enc)
            else:
                raise Exception("Encoding was neither str nor list of str...")
        # All objects can update the address, even if they have no encoding
        curraddr = instruction.nextaddress(curraddr)
    return "\n".join(outputdata) 

def matchlabel(tomatch):
    """ Determines if given token is a valid label or not. """
    if type(tomatch) != str:
        return False
    if tomatch in SYMTAB:
        raise Exception("Duplicate symbol: " + tomatch)
    return tomatch[len(tomatch)-1] is ":"

def matchopcode(tomatch):
    """ Determines if given token is a valid opcode or not. """
    if type(tomatch) != str:
        return False
    return tomatch in OPCODES

def matchdirective(tomatch):
    """ Determines if given token is a valid directive or not. """
    if type(tomatch) != str:
        return False
    if tomatch[0] is not ".":
        return False
    return tomatch in DIRECTIVES

def directivehandler(directiveline):
    """ Creates directive objects from parsing input tokens. """
    tokens = directiveline.split()
    directivetoken = tokens[0]
    argtokens = tokens[1:]
    if matchlabel(directivetoken):
        directivetoken = tokens[1]
        argtokens = tokens[2:]
    directiveclass = DIRECTIVES[directivetoken]
    # Rejoins the arguments (by spaces) then splits by comma instead
    if argtokens:
        argtokens = " ".join(argtokens).split(", ")
    directiveobj = directiveclass(argtokens)
    return directiveobj

def printsymtab():
    """ Displays the symbol nicely. """
    print "Symbol Table\n============"
    for key in SYMTAB:
        if type(SYMTAB[key]) is tuple:
            print "Symbol: '{0}' Value: {1}".format(key, SYMTAB[key])
        else:
            print "Symbol: '{0}'' Value: {1:#x}".format(key, int(SYMTAB[key]))

def opcodehandler(instructionline):
    """ 
    Creates the correct instruction object by parsing input tokens.

    Instructions are created by first looking up the opcode in a table to 
    find out what object class it belongs to, then searching specifically for
    the operands that that instruction requires. For example, an opcode token
    with the value 'addi' would be determined to require a destination register, 
    source register, and immediate value. The instruction would be parsed as such.
    """
    tokens = instructionline.split()
    opcodetoken = tokens[0]
    if matchlabel(opcodetoken):
        opcodetoken = tokens[1]
    if opcodetoken not in OPCODES:
        raise Exception(opcodetoken + " is not a valid opcode.")
    operandvalues = parseoperands(instructionline)
    opcode = OPCODES[opcodetoken]
    if opcodetoken in I_OPCODES:
        if opcodetoken in INSTRUCTIONS:
            instrclass = INSTRUCTIONS[opcodetoken]
            instrobj = instrclass(opcode, **operandvalues)
        else:
            instrobj = instructions.IType(opcode, **operandvalues)
    if opcodetoken in J_OPCODES:
        instrobj = instructions.JType(opcode, **operandvalues)
    if opcodetoken in R_OPCODES:
        funccode = R_FUNCCODES[opcodetoken]
        if R_OPCODES[opcodetoken] == 0:
            instrobj = instructions.RALU(opcode, funccode, **operandvalues)
        else:     
            instrobj = instructions.RFPU(opcode, funccode, **operandvalues)
    return instrobj

def parseoperands(instructionline):
    """ 
    Parses tokens in a line for their values. 

    Most of the heavy (parse)lifting is done here. Returning named values 
    allows instructions to be dynamically created by principle of which set of 
    operands they require. 
    """

    # opcode rd, offset(rs1)
    re1 = re.compile(r"\w+[ ]+[rRfF](\d{1,2}), (\d+)\([rRfF](\d{1,2})\)")
    m1 = re1.search(instructionline)
    if m1:
        rdest, immediate, rs1 = m1.groups()
        return {"rdest":int(rdest), "immediate": int(immediate), "rs1": int(rs1)}

    # opcode offset(rs1), rd
    re11 = re.compile(r"\w+[ ]+[rRfF](\d{1,2}), ((?![rRfF]\d{1,2})\D+\d*)")
    m11 = re11.search(instructionline)
    if m11:
        rdest, name = m11.groups()
        return {"rdest":int(rdest), "immediate":name}

    # opcode offset(rs1), rd
    re2 = re.compile(r"\w+[ ]+(-?\d+)\([rRfF](\d{1,2})\), [rRfF](\d{1,2})")
    m2 = re2.search(instructionline)
    if m2:
        immediate, rs1, rdest = m2.groups()
        return {"rdest":int(rdest), "immediate": int(immediate), "rs1":int(rs1)}

    # opcode immediate, rd
    re22 = re.compile(r"\w+[ ]+((?![rRfF]\d{1,2})\w+), [rRfF](\d{1,2})")
    m22 = re22.search(instructionline)
    if m22:
        immediate, rdest = m22.groups()
        return {"rdest":int(rdest), "immediate":immediate}
    
    # opcode rd, rs1
    re3 = re.compile(r"^\w+[ ]+[rRfF](\d{1,2}), [rRfF](\d{1,2})$")
    m3 = re3.search(instructionline)
    if m3:
        rdest, rs1 = m3.groups()
        return {"rdest":int(rdest), "rs1":int(rs1)}

    # opcode rd, rs1, rs2    
    re4 = re.compile(r"\w+[ ]+[rRfF](\d{1,2}), [rRfF](\d{1,2}), [rRfF](\d{1,2})")
    m4 = re4.search(instructionline)
    if m4:
        rdest, rs1, rs2 = m4.groups()
        return {"rdest":int(rdest), "rs1":int(rs1), "rs2":int(rs2)}

    # rd, rs1, immediate
    re5 = re.compile(r"\w+[ ]+[rRfF](\d{1,2}), [rRfF](\d{1,2}), (\w+)")
    m5 = re5.search(instructionline)
    if m5:
        rdest, rs1, immediate = m5.groups()
        return {"rdest":int(rdest), "rs1":int(rs1), "immediate":immediate}

    # opcode rd, immediate
    re6 = re.compile(r"\w+[ ]+[rRfF](\d{1,2}), (\d+)")
    m6 = re6.search(instructionline)
    if m6:
        rdest, immediate = m6.groups()
        return {"rdest":int(rdest), "immediate":int(immediate)}

    # opcode name
    re7 = re.compile(r"\w+[ ]+((?![rRfF]\d{1,2})\w+)")
    m7 = re7.search(instructionline)
    if m7:
        name, = m7.groups()
        return {"name":name}

    # opcode rs1
    re8 = re.compile(r"\w+[ ]+[rRfF](\d{1,2})")
    m8 = re8.search(instructionline)
    if m8:
        rs1, = m8.groups()
        return {"rs1":int(rs1)}
    
    # opcode rs1, name
    re9 = re.compile(r"[bB]\D*[ ]+[rRfF](\d{1,2}), ((?![rRfF]\d{1,2})\w+)")
    m9 = re9.search(instructionline)
    if m9:
        rs1, name = m9.groups()
        return {"rs1":int(rs1), "name":name}

    return {}
