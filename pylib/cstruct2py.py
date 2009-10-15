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

class cheaderfile(textfile):
    """Class to handle text file.
    
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

    def __get_enum(self):
        """Get all enumeration
        """
        fileStr = "".join(self.content)
        #Find all enumerations
        pattern = re.compile("enum.*?{.*?}", re.MULTILINE)
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
