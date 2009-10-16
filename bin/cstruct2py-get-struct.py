#!/usr/bin/env python2.5
"""This script reads struct from C/C++ header file and output query

Author ykk
Date June 2009
"""
import sys
import getopt
import cheader
import c2py


def usage():
    """Display usage
    """
    print "Usage "+sys.argv[0]+" <options> header_file struct_name\n"+\
          "Options:\n"+\
          "-h/--help\n\tPrint this usage guide\n"+\
          "-c/--cstruct\n\tPrint C struct\n"+\
          ""
          
#Parse options and arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hc",
                               ["help","cstruct"])
except getopt.GetoptError:
    usage()
    sys.exit(2)

#Check there is only 1 input file and struct name
if not (len(args) == 2):
    usage()
    sys.exit(2)
    
#Parse options
##Print C struct
printc = False
for opt,arg in opts:
    if (opt in ("-h","--help")):
        usage()
        sys.exit(0)
    elif (opt in ("-c","--cstruct")): 
        printc = True
    else:
        assert (False,"Unhandled option :"+opt)

headerfile = cheader.cheaderfile(args[0])
cstruct = headerfile.structs[args[1].strip()]
cs2p = c2py.cstruct2py()

if (printc):
    print cstruct

print "Python pattern = "+cs2p.get_pattern(cstruct)
