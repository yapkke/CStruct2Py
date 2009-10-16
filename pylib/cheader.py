"""This module parse and store a C/C++ header file.

Date June 2009
Created by ykk
"""
import re

class textfile:
    """Class to handle text file.
    
    Date June 2009
    Created by ykk
    """
    def __init__(self, filename):
        """Initialize filename with no content.
        """
        ##Filename
        self.filename = filename
        ##Content
        self.content = []

    def read(self):
        """Read file
        """
        fileRef = open(self.filename, "r")
        for line in fileRef:
            self.content.append(line)
        fileRef.close()        

class cprimitive:
    """Class to represent C primitive

    Date October 2009
    Created by ykk
    """
    def __init__(self,name, type):
        """Initialize and store primitive
        """
        ##Name
        self.name = name
        ##Type of primitive
        self.type = type
        
class cstruct:
    """Class to represent C struct

    Date October 2009
    Created by ykk
    """
    def __init__(self, name):
        """Initialize struct
        """
        ##Name of struct
        self.name = name
        ##List of members in struct
        self.members = []

class ctype_check:
    """Class to check c types

    Date October 2009
    Created by ykk
    """
    def __init__(self):
        """Initialize
        """
        self.CPrimitives = ["char","signed char","unsigned char",
                            "short","unsigned short",
                            "int","unsigned int",
                            "long","unsigned long",
                            "long long","unsigned long long",
                            "float","double",
                            "uint8_t","uint16_t","uint32_t","uint64_t"]

    def is_primitive(self,type):
        """Check type given is primitive.

        Return true if valid, and false otherwise
        """
        if (type in self.CPrimitives):
            return True
        else:
            return False

    def is_array(self, string):
        """Check if string declares an array
        """
        parts=string.strip().split()
        if (len(parts) <= 1):
            return False
        else:
            pattern = re.compile("\[.*?\]", re.MULTILINE)
            values = pattern.findall(string)
            if (len(values) == 1):
                return True
            else:
                return False

    def parse_type(self, string):
        """Parse string and return cstruct or cprimitive.
        Else return None
        """
        parts=string.strip().split()
        if (len(parts) == 0):
            return None
        print string.strip()+"\t"+str(self.is_array(string))

class cheaderfile(textfile):
    """Class to handle C header file.
    
    Date June 2009
    Created by ykk
    """
    def __init__(self, filename):
        """Initialize filename and read from file
        """
        textfile.__init__(self,filename)
        self.read()
        self.__remove_comments()
        ##Dictionary of macros
        self.macros = {}
        self.__get_macros()
        ##Dictionary of enumerations
        self.enums = {}
        self.enum_values = {}
        self.__get_enum()
        ##Dictionary of structs
        self.structs = {}
        self.__get_struct()

    def __remove_comments(self):
        """Remove all comments
        """
        fileStr = "".join(self.content)
        pattern = re.compile("\\\.*?\n", re.MULTILINE)
        fileStr = pattern.sub("",fileStr)
        pattern = re.compile(r"/\*.*?\*/", re.MULTILINE|re.DOTALL)
        fileStr = pattern.sub("",fileStr)
        pattern = re.compile("//.*$", re.MULTILINE)
        fileStr = pattern.sub("",fileStr)
        self.content = fileStr.split('\n')

    def __get_struct(self):
        """Get all structs
        """
        typecheck = ctype_check()
        fileStr = "".join(self.content)
        #Find all structs
        pattern = re.compile("struct[\w\s]*?{.*?};", re.MULTILINE)
        matches = pattern.findall(fileStr)
        #Process each struct
        namepattern = re.compile("struct(.+?)[ {]", re.MULTILINE)
        pattern = re.compile("{(.+?)};", re.MULTILINE)
        for match in matches:
            structname = namepattern.findall(match)[0].strip()
            values = pattern.findall(match)[0].strip().split(";")
            cstru = cstruct(structname)
            for val in values:
                cstru.members.append(typecheck.parse_type(val))
            self.structs[structname] = cstru
            print
        
    def __get_enum(self):
        """Get all enumeration
        """
        fileStr = "".join(self.content)
        #Find all enumerations
        pattern = re.compile("enum[\w\s]*?{.*?}", re.MULTILINE)
        matches = pattern.findall(fileStr)
        #Process each enumeration
        namepattern = re.compile("enum(.+?){", re.MULTILINE)
        pattern = re.compile("{(.+?)}", re.MULTILINE)
        for match in matches:
            values = pattern.findall(match)[0].strip().split(",")
            #Process each value in enumeration
            enumList = []
            value = 0
            for val in values:
                valList=val.strip().split("=")
                enumList.append(valList[0].strip())
                if (len(valList) == 1):
                    self.enum_values[valList[0].strip()] = str(value)
                    value += 1
                else:
                    self.enum_values[valList[0].strip()] = valList[1].strip()
            self.enums[namepattern.findall(match)[0].strip()] = enumList
        
    def __get_macros(self):
        """Extract macros
        """
        for line in self.content:
            if (line[0:8] == "#define "):
                lineList = line[8:].split()
                if (len(lineList) >= 2):
                    self.macros[lineList[0]] = "".join(lineList[1:])
                else:
                    self.macros[lineList[0]] = ""
