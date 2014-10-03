'''
Directives
===============

This module:
Maps directives to their respective class.
Implements functionality of assembler directives
'''

import struct, binascii




class Directive(object):
    ''' Base class for all Directive subtypes. '''
    def __init__(self, curraddr, args):
        self.curraddr = curraddr
        self.args = args

    def getlength(self):
        return self.length

class TextDirective(Directive):
    def nextaddress(self):
        if self.args:
            return int(self.args[0], 16)
        else:
            return 0

class DataDirective(Directive):
    def nextaddress(self):
        if self.args:
            return int(self.args[0], 16)
        else:
            return 0x200

class AlignDirective(Directive):
    def nextaddress(self):
        multof = pow(2, int(self.args[0]))
        if self.curraddr % multof == 0:
            return self.curraddr
        else:
            return (int(self.curraddr)/multof)*multof+multof

class AsciizDirective(Directive):
    def nextaddress(self):
        bytelength = 0
        for asciiword in self.args:
            bytelength = bytelength + len(asciiword.strip('",')) + 1
        return bytelength + self.curraddr

    def encode(self):
        encoding = []
        for asciiword in self.args:
            asciiword = asciiword.strip('",')    
            encoding.append((asciiword + '\0').encode('hex'))
        return encoding

class DoubleDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 8

    def encode(self):
        encoding = []
        for doubleval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>d', 
                float(doubleval.strip(',')))))
        return encoding

class FloatDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 4

    def encode(self):
        encoding = []
        for floatval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>f', 
                float(floatval.strip(',')))))
        return encoding

class WordDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 4

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
    def nextaddress(self):
        return self.curraddr + int(self.args[0])

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
