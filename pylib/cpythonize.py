"""This module generate Python code for C structs.

Date January 2010
Created by ykk
"""
import cheader
import c2py
import datetime
import struct

class rules:
    """Class that specify rules for pythonization

    Date January 2010
    Created by ykk
    """
    def __init__(self):
        """Initialize rules
        """
        ##Default values for members
        self.default_values = {}
        #Default values for struct
        self.struct_default = {}
        ##Macros to exclude
        self.excluded_macros = []
        ##Enforce mapping
        self.enforced_maps = {}

    def get_enforced_map(self, structname):
        """Get code to enforce mapping
        """
        code = []
        try:
            mapping = self.enforced_maps[structname]
        except KeyError:
            return None
        for (x,xlist) in mapping:
            code.append("if (not (self."+x+" in "+xlist+"_values)):")
            code.append("\treturn (False, \""+x+" must have values from "+xlist+"\")")
        return code
        

    def get_struct_default(self, structname, fieldname):
        """Get code to set defaults for member struct
        """
        try:
            return "."+fieldname+self.struct_default[(structname, fieldname)]
        except KeyError:
            return None
        
    def get_default_value(self, structname, fieldname):
        """Get default value for struct's field
        """
        try:
            return self.default_values[(structname, fieldname)]
        except KeyError:
            return 0

    def include_macro(self, name):
        """Check if macro should be included
        """
        return not (name in self.excluded_macros)

class pythonizer:
    """Class that pythonize C structures

    Date January 2010
    Created by ykk
    """
    def __init__(self, cheaderfile, pyrules = None):
        """Initialize
        """
        ##Rules
        if (pyrules == None):
            self.rules = rules()
        else:
            self.rules = pyrules
        ##Reference to C header file
        self.cheader = cheaderfile
        ##Reference to cstruct2py
        self.__c2py = c2py.cstruct2py()
        ##Code for assertion
        self.__assertcode = []

    def pycode(self,preamble=None):
        """Return pythonized code
        """
        code = []
        code.append("import struct")
        code.append("")
        if (preamble != None):
            fileRef = open(preamble,"r")
            for l in fileRef:
                code.append(l[:-1])
            fileRef.close()
        for name,struct in self.cheader.structs.items():
            code.extend(self.pycode_struct(struct))
            code.append("")
        for name,enum in self.cheader.enums.items():
            code.extend(self.pycode_enum(name,enum))
            code.append("")
        for name,macro in self.cheader.macros.items():
            code.extend(self.pycode_macro(name))
            code.append("")
        return code

    def pycode_enum(self, name, enum):
        """Return Python dict for enum
        """
        code=[]
        code.append(name+" = "+str(enum))
        ev = []
        for e in enum:
            v = self.cheader.get_value(e)
            ev.append(v)
            code.append(e+" = "+str(v))
        code.append(name+"_values = "+str(ev))
        return code

    def pycode_macro(self,name):
        """Return Python dict for macro
        """
        code = []
        if (self.rules.include_macro(name)):
            code.append(name+" = "+str(self.cheader.get_value(name)))
        return code

    def pycode_struct(self, struct_in):
        """Return Python class code given C struct.

        Returns None if struct_in is not cheader.cstruct.
        Else return list of strings that codes Python class.
        """
        if (not isinstance(struct_in, cheader.cstruct)):
            return None

        code=[]
        self.__assertcode = []
        code.extend(self.codeheader(struct_in))
        code.extend(self.codeinit(struct_in))
        code.append("")
        code.extend(self.codeassert(struct_in))
        code.append("")
        code.extend(self.codepack(struct_in))
        code.append("")
        code.extend(self.codeunpack(struct_in))
        return code

    def codeheader(self, struct_in):
        """Return Python code for header
        """
        code=[]
        code.append("class "+struct_in.typename+":")
        code.append("\t\"\"\"Automatically generated Python class for "+struct_in.typename)
        code.append("")
        code.append("\tDate "+str(datetime.date.today()))
        code.append("\tCreated by "+self.__module__+"."+self.__class__.__name__)
        code.append("\t\"\"\"")
        return code

    def codeinit(self, struct_in):
        """Return Python code for init function
        """
        code = []
        code.append("\tdef __init__(self):")
        code.extend(self.codemembers(struct_in,"\t\tself"))
        return code

    def codemembers(self, struct_in, prepend=""):
        """Return members of class
        """
        code = []
        for member in struct_in.members:
            if (isinstance(member, cheader.cstruct)):
                code.append(prepend+"."+member.name+" = "+member.typename+"()")
                struct_default = self.rules.get_struct_default(struct_in.typename, member.name)
                if (struct_default != None):
                    code.append(prepend+struct_default)
                self.__structassert(member, (prepend+"."+member.name).strip())
            elif (isinstance(member, cheader.carray)):
                if (member.typename == "char"):
                    initvalue = "\"\""
                    self.__stringassert(member, (prepend+"."+member.name).strip())
                else:
                    if (isinstance(member.object, cheader.cprimitive)):
                        initvalue="0"
                    else:
                        initvalue="None"
                    initvalue="["+(initvalue+",")*member.size
                    initvalue=initvalue[:-1]+"]"
                    self.__arrayassert(member, (prepend+"."+member.name).strip())
                code.append(prepend+"."+member.name+"= "+initvalue)
            else:
                code.append(prepend+"."+member.name+" = "+
                            str(self.rules.get_default_value(struct_in.typename, member.name)))
        return code

    def __structassert(self, cstruct, cstructname):
        """Return code to check for C array
        """
        self.__assertcode.append("\t\tif(not isinstance("+cstructname+", "+cstruct.typename+")):")
        self.__assertcode.append("\t\t\treturn (False, \""+cstructname+" is not class "+cstruct.typename+" as expected.\")")        

    def __addassert(self, prefix):
        code = []
        code.append(prefix+"if(not self.__assert()[0]):")
        code.append(prefix+"\treturn None")        
        return code

    def __stringassert(self, carray, carrayname):
        """Return code to check for C array
        """
        self.__assertcode.append("\t\tif(not isinstance("+carrayname+", str)):")
        self.__assertcode.append("\t\t\treturn (False, \""+carrayname+" is not string as expected.\")")        
        self.__assertcode.append("\t\tif(len("+carrayname+") > "+str(carray.size)+"):")      
        self.__assertcode.append("\t\t\treturn (False, \""+carrayname+" is of size "+str(carray.size)+" as expected.\")")

    def __arrayassert(self, carray, carrayname):
        """Return code to check for C array
        """
        self.__assertcode.append("\t\tif(not isinstance("+carrayname+", list)):")
        self.__assertcode.append("\t\t\treturn (False, \""+carrayname+" is not list as expected.\")")
        self.__assertcode.append("\t\tif(len("+carrayname+") != "+str(carray.size)+"):")
        self.__assertcode.append("\t\t\treturn (False, \""+carrayname+" is of size "+str(carray.size)+" as expected.\")") 

    def codeassert(self, struct_in):
        """Return code for sanity checking
        """
        code = []
        code.append("\tdef __assert(self):")
        enforce = self.rules.get_enforced_map(struct_in.typename)
        if (enforce != None):
            for line in enforce:
                code.append("\t\t"+line)
        code.extend(self.__assertcode)
        code.append("\t\treturn (True, None)")
        return code

    def codepack(self, struct_in, prefix="!"):
        """Return code that pack struct
        """
        code = []
        code.append("\tdef pack(self, assertstruct=True):")
        code.append("\t\tif(assertstruct):")
        code.extend(self.__addassert("\t\t\t"))
        code.append("\t\tpacked = \"\"")
        primPattern = ""
        primMemberNames = []
        for member in struct_in.members:
            if (isinstance(member, cheader.cprimitive)):
                #Primitives
                primPattern += self.__c2py.structmap[member.typename]
                primMemberNames.append("self."+member.name)
            else:
                (primPattern, primMemberNames) = \
                              self.__codepackprimitive(code, primPattern,
                                                       primMemberNames, prefix)
                if (isinstance(member, cheader.cstruct)):
                    #Struct
                    code.append("\t\tpacked += self."+member.name+".pack()")
                elif (isinstance(member, cheader.carray) and member.typename == "char"):
                    #String
                    code.append("\t\tpacked += self."+member.name+".ljust("+\
                                str(member.size)+",'\\0')")
                elif (isinstance(member, cheader.carray) and \
                      isinstance(member.object, cheader.cprimitive)):
                    #Array of Primitives
                    expandedarr = ""
                    for x in range(0, member.size):
                        expandedarr += ", self."+member.name+"["+\
                                       str(x).strip()+"]"
                    code.append("\t\tpacked += struct.pack(\""+prefix+\
                                self.__c2py.structmap[member.object.typename]*member.size+\
                                "\""+expandedarr+")")
                elif (isinstance(member, cheader.carray) and \
                      isinstance(member.object, cheader.cstruct)):
                    #Array of struct
                    for x in range(0, member.size):
                        code.append("\t\tpacked += self."+member.name+"["+\
                                    str(x).strip()+"].pack()")
        #Clear remaining fields
        (primPattern, primMemberNames) = \
                      self.__codepackprimitive(code, primPattern,
                                               primMemberNames, prefix)
        code.append("\t\treturn packed")
        return code

    def __codepackprimitive(self, code, primPattern, primMemberNames, prefix):
        """Return code for packing primitives
        """
        if (primPattern != ""):
            #Clear prior primitives
            code.append("\t\tpacked += struct.pack(\""+\
                        prefix+primPattern+"\", "+\
                        str(primMemberNames).replace("'","")[1:-1]+")")
        return ("",[])

    def codeunpack(self, struct_in, prefix="!"):
        """Return code that unpack struct
        """
        pattern = self.__c2py.get_pattern(struct_in)
        structlen = self.__c2py.get_size(pattern)
        code = []
        code.append("\tdef unpack(self, binaryString):")
        code.append("\t\tif (len(binaryString) < "+str(structlen)+"):")
        code.append("\t\t\treturn binaryString")
        offset = 0
        primPattern = ""
        primMemberNames = []
        for member in struct_in.members:
            if (isinstance(member, cheader.cprimitive)):
                #Primitives
                primPattern += self.__c2py.structmap[member.typename]
                primMemberNames.append("self."+member.name)
            else:
                (primPattern, primMemberNames, offset) = \
                              self.__codeunpackprimitive(code, offset, primPattern,
                                                         primMemberNames, prefix)
                if (isinstance(member, cheader.cstruct)):
                    #Struct
                    code.append("\t\tself."+member.name+\
                                ".unpack(binaryString["+str(offset)+":])")
                    pattern = self.__c2py.get_pattern(member)
                    offset += self.__c2py.get_size(pattern)
                elif (isinstance(member, cheader.carray) and member.typename == "char"):
                    #String
                    code.append("\t\tself."+member.name+\
                                " = binaryString["+str(offset)+":"+\
                                str(offset+member.size)+"].replace(\"\\0\",\"\")")
                    offset += member.size
                elif (isinstance(member, cheader.carray) and \
                      isinstance(member.object, cheader.cprimitive)):
                    #Array of Primitives
                    expandedarr = ""
                    arrpattern = self.__c2py.structmap[member.object.typename]*member.size
                    for x in range(0, member.size):
                        expandedarr += "self."+member.name+"["+\
                                       str(x).strip()+"], "
                    code.append("\t\t("+expandedarr[:-2]+") = struct.unpack_from(\""+\
                                prefix+arrpattern+\
                                "\", binaryString, "+str(offset)+")")
                    offset += struct.calcsize(arrpattern)
                elif (isinstance(member, cheader.carray) and \
                      isinstance(member.object, cheader.cstruct)):
                    #Array of struct
                    astructlen = self.__c2py.get_size(self.__c2py.get_pattern(member.object))
                    for x in range(0, member.size):
                        code.append("\t\tself."+member.name+"["+str(x)+"]"+\
                                ".unpack(binaryString["+str(offset)+":])")
                        offset += astructlen
        #Clear remaining fields
        (primPattern, primMemberNames, offset) = \
                      self.__codeunpackprimitive(code, offset, primPattern,
                                                 primMemberNames, prefix)
        code.append("\t\treturn binaryString["+str(structlen)+":]");
        return code

    def __codeunpackprimitive(self, code, offset, primPattern,
                              primMemberNames, prefix):
        """Return code for unpacking primitives
        """
        if (primPattern != ""):
            #Clear prior primitives
            code.append("\t\t("+str(primMemberNames).replace("'","")[1:-1]+\
                        ") = struct.unpack_from(\""+\
                        prefix+primPattern+"\", binaryString, "+str(offset)+")")
        return ("",[], offset+struct.calcsize(primPattern))

