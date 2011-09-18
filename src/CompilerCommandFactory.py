__author__ = "Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "14 September 2002"

import os

# This list make an association between compiler names and their respective
# CompilerCommand filename/class name

compiler_assocciation = {
    "gcc"       : ("CompilerCommand_c", "CompilerCommand_c"),
    "cc"        : ("CompilerCommand_c", "CompilerCommand_c"),
    "g++"       : ("CompilerCommand_cpp", "CompilerCommand_cpp"),
    "cxx"       : ("CompilerCommand_cpp", "CompilerCommand_cpp")
    }

def build_compiler_instance(command_args):
    compiler_name = os.path.basename(command_args[0])
    try:
        compiler = compiler_assocciation[compiler_name]
    except KeyError:
        # raise an excetpion to tell it's a unknown Compiler
        print "The compiler " + compiler_name + " is unknown"
        raise
    
    exec "import " + compiler[0]
    ##__import__(compiler[0])
    #FIXME : maybe there is a better way to instanciate a classe from a string
    exec "res = "+ compiler[1] + "." + compiler[1] +\
         "(command_args)"
    return res
