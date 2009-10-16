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

class ctype:
    """Class to represent types in C
    """
    def __init__(self,typename, name=None, expanded=False):
        """Initialize
        """
        ##Name
        self.name = name
        ##Type of primitive
        self.typename = typename
        ##Expanded
        self.expanded = expanded

class cprimitive(ctype):
    """Class to represent C primitive

    Date October 2009
    Created by ykk
    """
    def __init__(self,typename, name=None):
        """Initialize and store primitive
        """
        ctype.__init__(self, typename, name, True)

    def __str__(self):
        """Return string representation
        """
        if (self.name == None):
            return self.typename
        else:
            return self.typename+" "+str(self.name)
        
class cstruct(ctype):
    """Class to represent C struct

    Date October 2009
    Created by ykk
    """
    def __init__(self, typename, name=None):
        """Initialize struct
        """
        ctype.__init__(self, typename, name)
        ##List of members in struct
        self.members = []
    
    def __str__(self):
        """Return string representation
        """
        string = "struct "+self.typename+" "
        if (self.name != None):
            string += self.name+" "
        if (len(self.members) == 0):
            return string
        #Add members
        string +="{\n"
        for member in self.members:
            string += "\t"+str(member)+"\n"
        string +="};"
        return string

class carray(ctype):
    """Class to represent C array

    Date October 2009
    Created by ykk
    """
    def __init__(self, typename, name, isPrimitive, size):
        """Initialize array of object.
        """
        ctype.__init__(self, typename, name,
                       (isinstance(size, int) and isPrimitive))
        ##Object reference
        if (isPrimitive):
            self.object = cprimitive(typename, name)
        else:
            self.object = cstruct(typename, name)
        ##Size of array
        self.size = size

class ctype_parser:
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

    def parse_array(self, string):
        """Parse array from string.
        Return occurrence and name.
        """
        pattern = re.compile("\[.*?\]", re.MULTILINE)
        namepattern = re.compile(".*?\[", re.MULTILINE)
        values = pattern.findall(string)
        if (len(values) != 1):
            return (1,string)
        else:
            val = values[0][1:-1]
            try:
                sizeval = int(val)
            except ValueError:
                sizeval = val
            return (sizeval,
                    namepattern.findall(string)[0].strip()[0:-1])

    def parse_type(self, string):
        """Parse string and return cstruct or cprimitive.
        Else return None
        """
        parts=string.strip().split()
        if (len(parts) >= 2):
            if (parts[0].strip() == "struct"):
                typename = " ".join(parts[1:-1])
            else:
                typename = " ".join(parts[:-1])
            (size, name) = self.parse_array(parts[-1])
            if (size == 0):
                return None
            #Create appropriate type
            if (size > 1):
                #Array
                return carray(typename, name, 
                              self.is_primitive(typename),size)
            else:
                #Not array
                if (self.is_primitive(typename)):
                    return cprimitive(typename, name)
                else:
                    return cstruct(typename, name)
        else:
            return None

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
        typeparser = ctype_parser()
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
                presult = typeparser.parse_type(val)
                if (presult != None):
                    cstru.members.append(presult)
            self.structs[structname] = cstru

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
