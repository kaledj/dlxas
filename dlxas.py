#!/usr/bin/python

'''
dlxas.py
========
The DLX assembler. 

Usage: python dlxas.py filename
'''

import sys, os
# User modules
import dlxparser

def main():
    ''' Main function. Checks arguments and runs. '''
    args = sys.argv
    if args[1]:
        filename, extension = os.path.splitext(args[1])
        if extension != ".dlx":
            sys.exit("Please supply a valid .dlx file")
    else: 
        sys.exit("Please provide an input file.")

    try: 
        with open(args[1], 'r') as infile:
            inputdata = infile.read()
        outputdata = dlxparser.parse(inputdata)
        with open(filename + "TEST.hex", 'w') as outfile:
            outfile.write(outputdata)
    except IOError, exc:
        sys.exit(str(exc))

if __name__ == '__main__':
    main()
