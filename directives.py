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
        multof = int(self.args[0]**2)
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
            encoding.append((asciiword + '\0').encode('hex'))
        return encoding

class DoubleDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 8

    def encode(self):
        encoding = []
        for doubleval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>d'), 
                float(doubleval.strip(','))))
        return encoding

class FloatDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 4

    def encode(self):
        encoding = []
        for floatval in self.args:    
            encoding.append(binascii.hexlify(struct.pack('>f'), 
                float(floatval.strip(','))))
        return encoding

class WordDirective(Directive):
    def nextaddress(self):
        return self.curraddr + len(self.args) * 4

    def encode(self):
        encoding = []
        for intval in self.args:    
            encoding.append("%08x" %(intval.strip(',')))
        return encoding

class SpaceDirective(Directive):
    def nextaddress(self):
        return self.curraddr + self.args[0]

DIRECTIVES = {
        ".text": TextDirective, 
        ".data": DataDirective, 
        ".align": AlignDirective, 
        ".asciiz": AsciizDirective, 
        ".double": DoubleDirective, 
        ".float": FloatDirective, 
        ".word": WordDirective, 
        ".space": SpaceDirective
    }
