"""
Directives
==========

Provides a directive type and strategies for their functionality. 

This module:
1) Provides a types for all DLX directives. Directives are responsible for 
        knowing how they modify the current address during assembly. Also, 
        any directive that has an encoding is responsible for knowing how to 
        encode, e.g. a .asciiz directive will need to provide the multiple 
        lines of hex values that encode the ascii values given by the directive.
2) Provides factory-like functionality. A constant mapping is given that maps
        directive strings like ".text" to their object class. For example, 
        ".text" --> <type directives.TextDirective>.  
"""

import struct, binascii

class Directive(object):
    """
    Base class for all directives. 

    This base class only implements common initialization functionality that is 
    shared by all directives. All directive objects are initialized with a list 
    of arguments. These arguments are to be passed as a list of individual 
    tokens, where each token corresponds to one single argument. 
    All subtypes must implement <function nextaddress> with two parameters, 
    and may implement <function nextaddresses> with two parameters. This allows
    for them to be called the same way, even if they implement the method in a 
    different way.
    """
    def __init__(self, args):
        self.args = args

    def encode(self):
        """ 
        Base encoding functionality shared by all types. 
        
        Returns an empty string because directives that do not have a 
        manifestation such as .text can choose not to implement encode
        functionality, and instead inherit this. 
        """
        return ""

class TextDirective(Directive):
    """
    Implements functionality for the .text directive.

    This sets the address of the next instruction to n, which will be the only
    token in the arguments list. If no arguments are given, the address of the 
    next instruction is set to 0. 
    """
    def nextaddress(self, curraddr):
        if self.args:
            return int(self.args[0], 16)
        return 0

class DataDirective(Directive):
    """
    Implements functionality for the .data directive.

    This sets the address of the next data item to n, which will be the only 
    token in the argument list. If none are given, the address of the next data 
    item will be set to 0x200.
    """
    def nextaddress(self, curraddr):
        if self.args:
            return int(self.args[0], 16)
        return 0x200

class AlignDirective(Directive):
    def nextaddress(self, curraddr):
        multof = pow(2, int(self.args[0]))
        if curraddr % multof == 0:
            return curraddr
        else:
            return (int(curraddr)/multof)*multof+multof

class AsciizDirective(Directive):
    def nextaddress(self, curraddr):
        bytelength = 0
        for asciiword in self.args:
            bytelength = bytelength + len(asciiword.strip('"')) + 1
        return bytelength + curraddr

    def nextaddresses(self, curraddr):
        addresses = [curraddr]
        for asciiword in self.args:
            wordlen = len(asciiword.strip('"')) + 1
            addresses.append(curraddr + wordlen)
            curraddr = curraddr + wordlen
        return addresses

    def encode(self):
        encoding = []
        for asciiword in self.args:
            asciiword = asciiword.strip('"')    
            encoding.append((asciiword + '\0').encode('hex'))
        return encoding

class DoubleDirective(Directive):
    def nextaddress(self, curraddr):
        return curraddr + len(self.args) * 8

    def nextaddresses(self, curraddr):
        addresses = [curraddr]
        for val in self.args:
            addresses.append(curraddr + 8)
            curraddr = curraddr + 8
        return addresses

    def encode(self):
        encoding = []
        for doubleval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>d', 
                float(doubleval.strip(',')))))
        return encoding

class FloatDirective(Directive):
    def nextaddress(self, curraddr):
        return curraddr + len(self.args) * 4

    def nextaddresses(self, curraddr):
        addresses = [curraddr]
        for val in self.args:
            addresses.append(curraddr + 4)
            curraddr = curraddr + 4    
        return addresses

    def encode(self):
        encoding = []
        for floatval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>f', 
                float(floatval.strip(',')))))
        return encoding

class WordDirective(Directive):
    def nextaddress(self, curraddr):
        return curraddr + len(self.args) * 4

    def nextaddresses(self, curraddr):
        addresses = [curraddr]
        for val in self.args:
            addresses.append(curraddr + 4)
            curraddr = curraddr + 4
        return addresses

    def encode(self):
        encoding = []
        for intval in self.args:    
            if '0x' in intval:
                asstring = binascii.hexlify(struct.pack('>i', 
                    int(intval.strip(','), 16)))
            else:
                asstring = binascii.hexlify(struct.pack('>i', 
                    int(intval.strip(','))))
            encoding.append(asstring)
        return encoding


class SpaceDirective(Directive):
    def nextaddress(self, curraddr):
        return curraddr + int(self.args[0])

DIRECTIVES = {} 
def mapdirectives():
    ''' Performs the mapping to initialize DIRECTIVES. '''
    DIRECTIVES[".text"] = TextDirective 
    DIRECTIVES[".data"] = DataDirective 
    DIRECTIVES[".align"] = AlignDirective 
    DIRECTIVES[".asciiz"] = AsciizDirective 
    DIRECTIVES[".double"] = DoubleDirective 
    DIRECTIVES[".float"] = FloatDirective
    DIRECTIVES[".word"] = WordDirective
    DIRECTIVES[".space"] = SpaceDirective
mapdirectives()
