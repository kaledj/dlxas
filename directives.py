"""
Directives
==========

Provides a directive type and strategies for their functionality. 

This module:
1) Provides a types for all DLX directives. Directives are responsible for 
        knowing how they modify the current address during assembly. Also, 
        any directive that has an encoding is responsible for knowing how to 
        encode, e.g. a .asciiz directive will need to provide the multiple 
        lines of hex that encode the ascii values given by the directive.
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

    def nextaddress(self, curraddr, datasize):
        """ 
        Increments address by total length of all given data. 

        This is a base functionality that will be called by subclasses, with
        a different datasize depending on the subclass. 
        """
        return curraddr + len(self.args) * datasize

    def nextaddresses(self, curraddr, datasize):
        """
        Creates a list of addresses for each given data item. 

        This is a base functionality that will be called by the subclasses.
        Multiple directives insert multiple pieces of datasize size data, 
        so this functionality can be reused. Subclasses may called with 
        varying parameters to achieve their functionality. 
        """
        return [curraddr+(datasize*x) for x in range(len(self.args))]

    def encode(self):
        """ 
        Base encoding functionality shared by all types. 
        
        Returns an empty string because directives that do not have a 
        manifestation such as .text can choose not to implement encode
        functionality, and instead inherit this. 
        """
        return ""

    def encodef(self, formatstring):
        """ 
        Base encoding functionality for data inserting directives. 
        
        Each subclasses may make a call to this with different parameters 
        depending on how they need to be formatted, e.g. as decimal, hex, etc. 
        """
        encoding = []
        for val in self.args:    
            val = val.strip(', ')
            if 'i' in formatstring:
                if '0x' in val:
                    val = int(val, 16)
                else: 
                    val = int(val)
            else:
                val = float(val)
            asstring = binascii.hexlify(struct.pack(formatstring, val))
            encoding.append(asstring)
        return encoding

class TextDirective(Directive):
    """
    Implements functionality for the .text directive.

    Sets the address of the next instruction to n, which will be the only
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

    Sets the address of the next data item to n, which will be the only 
    token in the argument list. If none are given, the address of the next data 
    item will be set to 0x200.
    """

    def nextaddress(self, curraddr):
        if self.args:
            return int(self.args[0], 16)
        return 0x200

class AlignDirective(Directive):
    """
    Implements functionality for the .align directive. 

    Sets the next address to the next highest address with lower n bits 0. 
    This corresponds to rounding up to the next address with address 2^n. Does
    not change the address if it is already at that address. 
    """

    def nextaddress(self, curraddr):
        multof = pow(2, int(self.args[0]))
        if curraddr % multof == 0:
            return curraddr
        return (int(curraddr)/multof)*multof+multof

class AsciizDirective(Directive):
    """
    Implements functionality for the .asciiz directive. 

    Stores null terminated strings in memory. Arguments list will have n>0 
    tokens that each contain a string. 
    """

    def nextaddress(self, curraddr):
        """ Increments address by the total length of all given strings. """ 
        bytelength = 0
        for asciiword in self.args:
            bytelength = bytelength + len(asciiword.strip('"')) + 1
        return bytelength + curraddr

    def nextaddresses(self, curraddr):
        """ Gives a list of address on which each string will be inserted. """ 
        addresses = [curraddr]
        for asciiword in self.args:
            wordlen = len(asciiword.strip('"')) + 1
            addresses.append(curraddr + wordlen)
            curraddr = curraddr + wordlen
        return addresses

    def encode(self):
        """
        Provides an encoding for this directive. 

        Returns a list of encodings, each of which corresponds to a string. 
        Multiple individual arguments correspond to multiple lines of encoding. 
        However, multiple words in an argument all go on the same line. Null 
        terminator is added to the end of each string. 
        """
        encoding = []
        for asciiword in self.args:
            asciiword = asciiword.strip('"')    
            encoding.append((asciiword + '\0').encode('hex'))
        return encoding

class DoubleDirective(Directive):
    """
    Implements functionality for the .double directive. 

    Stores given doubles in memory. Must have n>0 argument tokens. 
    """

    def nextaddress(self, curraddr):
        return super(DoubleDirective, self).nextaddress(curraddr, 8)

    def nextaddresses(self, curraddr):
        return super(DoubleDirective, self).nextaddresses(curraddr, 8)

    def encode(self):
        return super(DoubleDirective, self).encodef('>d')

class FloatDirective(Directive):
    """
    Implements functionality for the .float directive. 

    Stores given floats in memory. Must have n>0 argument tokens. 
    """

    def encode(self):
        return super(FloatDirective, self).encodef('>f')

    def nextaddress(self, curraddr):
        return super(FloatDirective, self).nextaddress(curraddr, 4)

    def nextaddresses(self, curraddr):
        return super(FloatDirective, self).nextaddresses(curraddr, 4)

class WordDirective(Directive):
    """
    Implements functionality for the .word directive. 

    Stores given integers in memory. Must have n>0 argument tokens. 
    """

    def encode(self):
        return super(WordDirective, self).encodef('>i')

    def nextaddresses(self, curraddr):
        return super(WordDirective, self).nextaddresses(curraddr, 4)

    def nextaddress(self, curraddr):
        return super(WordDirective, self).nextaddress(curraddr, 4)

class SpaceDirective(Directive):
    """
    Implements functionality for the .space directive. 

    Increments address by amount given in n. Arguments must contain >0 tokens. 
    """
    
    def nextaddress(self, curraddr):
        return curraddr + int(self.args[0])

DIRECTIVES = {} 
def mapdirectives():
    """ Performs the mapping to initialize DIRECTIVES. """
    DIRECTIVES[".text"] = TextDirective 
    DIRECTIVES[".data"] = DataDirective 
    DIRECTIVES[".align"] = AlignDirective 
    DIRECTIVES[".asciiz"] = AsciizDirective 
    DIRECTIVES[".double"] = DoubleDirective 
    DIRECTIVES[".float"] = FloatDirective
    DIRECTIVES[".word"] = WordDirective
    DIRECTIVES[".space"] = SpaceDirective
mapdirectives()
