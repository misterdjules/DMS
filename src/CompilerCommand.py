"""This class is a template class to implement a new compiler.
When you have to implement a new compiler, simply overloaded the required
methods to fit your needs.
The new CompilerCommand class must derivate from this class (this interface)
The convention is to call the new CompilerCommand class like this:
CompilerCommand_nameofthecompiler into the file
CompilerCommand_nameofthecompiler.py"""

__author__      = "Julien Barbot <julien.barbot@laposte.net>\
                  and Julien Gilli <jgilli@nerim.fr>"
__version__     = "0.0"
__date__        = "14 September 2002"



class MustImplementMethod:
    """This class is used to force the definition of some methods
    This is to have a a similar behavior as
    virtual foo() const = 0 in C++"""
    pass

class CompilerCommand:
    "This is the interface that each new compiler must fit""" 

    def __init__(self, command_arguments):
        """command_arguments is a list composed by all arguments
        of the compiler command, executable name (sys.argv[0] included)
        Here, you have to initialise the attributes to None etc ..."""
    
    def is_distributable(self):
        """Return true if the command can be executed remotely,
        false otherwise.
        For example A compilation can be done remotely if it doesn't need
        linking.(in C)
        Here we should have something like this :
        if self.__is_distributable != None:
            return self.__is_distributable
        else
            do something to tell if it's distributable or not
        """
        raise MustImplementMethod

    def get_output_file_name_for_step(self, input_file, stop_step):
        """Take a filename as input, and return the name of the file
        that will be output if we execute the command.
        For example with gcc : gcc -stop_step filename."""
        raise MustImplementMethod
    
    def get_command_args(self):
        """return the arguments of the command line, the name of
        the executable is included"""
        raise MustImplementMethod

    def get_after_preprocessing_options(self):
        """Return the arguments list of the command line,
        except those that are used only at preprocessing level.
        If the currently implemented compiler doesn't have de preprocessing
        step, then simply return the command line"""
        raise MustImplementMethod

    def get_stop_step(self):
        """Return the stop step of the current command line"""
        raise MustImplementMethod

    def canonize_command(self):
        """Return a tuple of commands whose execution has the same
        effect as the original command. It is used to distribute a
        command which take several commands as input.
        For example, the following command :
        gcc -c test.c foo.c bar.c baz.c
        can be canonized as :
        (gcc -c test.c, gcc -c foo.c, gcc -c bar.c, gcc -c baz.c)
        FIXME: Not yet implemented
        """
        assert 0, "NOT YET IMPLEMENTED !"
        raise MustImplementMethod

    def replace_input_files(self, new_input_files):
        """Replace the input files name in input_files.keys()
        by their corresponding values in input_files.values()."""
        raise MustImplementMethod

    def do_preprocessing_step(self):
        """Return one tuple of tuples that  match filename
        as in the original command line with a temporary file
        object used to hold the preprocessed data.
        For example, the following command line :
        gcc -c test.c foo.i bar.S baz.s
        will return :
        ((temp_file_object, "test.c"),
        (foo.i_file_object, "foo.i"),
        (temp_file_object, "bar.S"),
        (baz.s_file_object, "baz.s")
        )
        If one of the preprocessing step exit with an error code != 0,
        we exit with the same exit code and delete the temporary files created
        so far.
        """
        raise MustImplementMethod

    def get_local_compiler_path(self):
        """This method must return the true path of the right compiler
        for example, if we are implementing the c++ class we have to return
        something like this : "/usr/bin/g++"
        Avoid simply returning something like "g++" because if it will create
        a loop (because g++ is a link to the DMS Compiler ...)
        """
        raise MustImplementMethod
        
        
