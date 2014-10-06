"""
DLX Assembler
========

This module handles user input and file IO. 
User input is validated first. Then, input file is opened and read, its contents
being passed to dlxparser for further processing.

"""

import sys, os
import dlxparser

def main():
    """ Main function. Checks arguments and begins execution. """
    args = sys.argv
    if args[1]:
        filepath, extension = os.path.splitext(args[1])
        if extension != ".dlx":
            sys.exit("Please supply a valid .dlx file")
    else: 
        sys.exit("Please provide an input file.")

    try: 
        with open(args[1], "r") as infile:
            inputdata = infile.read()
        outputdata = dlxparser.run(inputdata)
        with open(filepath + ".hex", "w") as outfile:
            outfile.write(outputdata)
    except IOError, exc:
        sys.exit(str(exc))

if __name__ == "__main__":
    main()
