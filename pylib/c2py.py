"""This module converts C types to Python struct pattern string.

Date June 2009
Created by ykk
"""
import cheader
import struct

class cstruct2py:
    """Class converts C struct to Python struct pattern string

    Date October 2009
    Created by ykk
    """
    def __init__(self):
        """Initialize
        """
        ##Mapping
        self.structmap = {}
        self.structmap["char"] = "c"
        self.structmap["signed char"] = "b"
        self.structmap["uint8_t"]=\
            self.structmap["unsigned char"] = "B"
        self.structmap["short"] = "h"
        self.structmap["uint16_t"] =\
            self.structmap["unsigned short"] = "H"
        self.structmap["int"] = "i"
        self.structmap["unsigned int"] = "I"
        self.structmap["long"] = "l"
        self.structmap["uint32_t"] =\
            self.structmap["unsigned long"] = "L"
        self.structmap["long long"] = "q"
        self.structmap["uint64_t"] =\
            self.structmap["unsigned long long"] = "Q"
        self.structmap["float"] = "f"
        self.structmap["double"] = "d"

    def get_pattern(self,ctype):
        """Get pattern string for ctype.
        Return None if ctype is not expanded.
        """
        if (ctype.expanded):
            if (isinstance(ctype, cheader.cprimitive)):
                return self.structmap[ctype.typename]
            elif (isinstance(ctype, cheader.cstruct)):
                string=""
                for member in ctype.members:
                    string += self.get_pattern(member)
                return string
            elif (isinstance(ctype, cheader.carray)):
                string = self.get_pattern(ctype.object)
                return string * ctype.size
        return None
        
    def get_size(self, ctype):
        """Return size of struct or pattern specified
        """
        if (isinstance(ctype, str)):
            return struct.calcsize(ctype)
        else:
            return struct.calcsize(self.get_pattern(ctype))

