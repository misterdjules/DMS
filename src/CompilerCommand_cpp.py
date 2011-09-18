""" For everything that could be confuse or difficult to understand in this
module, *please refer to the gcc info documentation*. Read carefully the subsection
Overall Options of the section Invoking GCC."""

__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "6 August 2002"

import FileUtils
import ListUtils
import tempfile
import sys
import os
import syslog
import CompilerCommand
import Configuration
import commands

def is_only_preprocessing_option(option):
    """Return true if the option "option" is usefull
    only at preprocessing level.
    It is mainly aimed at handling correctly the options that output
    dependency files in the directory of the program sources,
    like -Wp,-MD,.deps/foo.TPo.
    """
    # FIXME: add all the options that are specific to the preprocessing step
    only_preprocessing_options = (
        ("-Wp", 3),
        )

    for (only_preprocessing_option, length) in only_preprocessing_options:
        if option[:length] == only_preprocessing_option:
            return 1
    return 0


def get_preprocessing_options(options):
    """Filter the options tuple given by the options parameter
    and return the ones that are usefull for preprocessing
    """
    preprocessing_options = []
    for option in options:
        if option not in\
               CompilerCommand_cpp.compilation_stop_level_by_option.keys()\
               and option != "-o":
            preprocessing_options.append(option)
    return tuple(preprocessing_options)



def get_start_step_of_file(input_file):
    """Return an integer which represent at which step
    gcc will start the c
    ompilation process for this file
    1 is starting at the preprocessing level
    2 is starting at the compilation level
    3 is starting at the assembly level
    """

    # Put here any known extensions for c++ source files
    
    start_step_by_extension = {
        ".cc" : 1,
        ".cpp" : 1,
        ".cxx" : 1,
        ".S" : 1,
        ".i" : 2,
        ".s" : 3
        }
    file_extension = FileUtils.get_file_extension(input_file)
    if file_extension in start_step_by_extension.keys():
        return start_step_by_extension[file_extension]
    # unknown extension for the gcc C compiler, so consider
    # start step will be linking
    return 4


class CompilerCommand_cpp(CompilerCommand.CompilerCommand):
    """This class is aimed at manipulating a typical command line as
    processed by gcc version 2.95.3.
    It is instanciated by an instance of the Compiler class, and then
    used by this compiler to get various informations about that command and
    to transform it.
    For example, it can be used to know wether a command is distributable or to
    replace the original input filename by the preprocessed one.
    """

    # Associate a gcc command line option with a step where the compiler will
    # end his work.
    # 1 means that the compiler will stop before the compilation step.
    # 2 means that the compiler will stop before the assembly step
    # 3 means that the compiler will stop before the linking step
    # No option means that it will go through all steps (including linking)
    compilation_stop_level_by_option = {
        "-M" : 1,
        "-MM" : 1,
        "-MF" : 1,
        "-MG" : 1,
        "-MP" : 1,
        "-MT" : 1,
        "-MQ" : 1,
        "-MD" : 1,
        "-MMD" : 1,
        "-E" : 1,
        "-c" : 3,
        "-S" : 2
        }
    # Below are gcc options that make a command not distributable
    # what about --target-help ?
    # FIXME: add remaining non distributable options
    not_distributable_options = ["-ftest-coverage", "-fprofile-arcs",
                                 "-###", "--help", "--target-help"
                                 ]

    def __init__(self, command_arguments):
        """command_arguments is a list composed by all arguments
        of the compiler command, executable name (sys.argv[0] included)"""
        # FIXME is this really always true ?
        # Are there other possible command names ?
        #assert command_arguments[0][:3] == "gcc", "GCC class used for command\
        # name : " + command_arguments[0] + "." 
        self.__command_arguments = command_arguments

        # keep the input files as a cache, see get_input_files method
        # contains zero to several tupes of the following form :
        # (i, file) where i is the index of the file in the arguments list
        # and file is the file name
        self.__input_files = None
        
        # The files where the result of the command must be output.
        # This is set to None by default, to show that we haven't
        # used get_output_file yet
        # It contains tuples of the following forms :
        # (i, file) where i is the index of the file in the arguments list and file
        # is the file name
        self.__output_file = None

        # Indicate at which step the compilation process will start
        # (see above for details)
        self.__start_step = None

        # Indicate at which step the compilation process will stop
        # (see above for details)
        self.__stop_step = None

        # Indicate wether the command is distributable or not
        self.__is_distributable = None

        #Contain every options on the command line
        self.__options = None

    def get_command_args(self):
        """return the arguments of the command line, the name of
        the executable is included"""
        return self.__command_arguments
    
    def get_after_preprocessing_options(self):
        """Return the arguments list of the command line,
        except those that are used only at preprocessing level."""
        arguments = [] 
        for option in self.__command_arguments:
            if not is_only_preprocessing_option(option):
                arguments.append(option)
        return tuple(arguments)
    
    def get_output_file_name_for_step(self, input_file, stop_step):
        """Take a filename as input, and return the name of the file
        that will be output if we execute the command :
        gcc -stop_step filename."""
        
        # associate a stop level to the corresponding output
        # filename extension
        # 1 is stoping after preprocessing and before compilation
        # 2 is stoping after compilation and before assembly
        # 3 is stoping after assembly and before linking
        output_extensions = {
            1 : ".i",
            2 : ".s",
            3 : ".o"
            }
        
        start_level = get_start_step_of_file(input_file)
        if start_level > stop_step:
            # here we want the compilation process to stop when it starts,
            # so nothing is output
            return ""
        else:
            new_ext = output_extensions[stop_step]
            return FileUtils.strip_file_extension(input_file) + new_ext
        
    def get_stop_step(self):
        if self.__stop_step != None:
            return self.__stop_step
        self.__stop_step = 4
        for arg in self.__command_arguments[1:]:
            if arg in \
                   CompilerCommand_cpp.compilation_stop_level_by_option.keys() \
                   and CompilerCommand_cpp.compilation_stop_level_by_option[arg]\
                   < self.__stop_step:
                self.__stop_step = CompilerCommand_cpp.\
                                   compilation_stop_level_by_option[arg]
        return self.__stop_step
                
    
    def is_distributable(self):
        """Return true if the command can be executed remotely,
        false otherwise.
        A compilation can be done remotely if it doesn't need linking.
        """
        # if this has already been determinated, return the
        # cached value
        if self.__is_distributable != None:
            return self.__is_distributable
        if self.get_stop_step() < 4 \
           and self.get_stop_step() > 1 \
           and self.has_distributable_start_step() \
           and (ListUtils.get_intersection(\
            CompilerCommand_cpp.not_distributable_options,\
            self.__command_arguments) == []):
            self.__is_distributable = 1
        else:
            self.__is_distributable = 0
        return self.__is_distributable
        
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
        
    def get_input_files(self):
        """Return a tuple of tuples that contain every input files
        passed to the command, as wall as their index in the
        command arguments. This index can be used to easily replace
        filenames"""
        # use the cached value
        if self.__input_files != None:
            return tuple(self.__input_files)
        i = 0
        self.__input_files = []
        for arg in self.__command_arguments[1:]:
            # FIXME check if this is a sufficient test
            if (arg[0] != '-') \
                   and (i > 0 and (self.__command_arguments[i] != "-o")):
                # use i + 2 as the index for the file because we start the loop
                # from index 1 of the arguments list
                self.__input_files.append((i + 1, arg))
            i = i + 1    
        return tuple(self.__input_files)
            
    def replace_input_files(self, new_input_files):
        """Replace the input files name in input_files.keys()
        by their corresponding values in input_files.values()."""
        for original_file_name in new_input_files.keys():
            index_in_args = self.__command_arguments.index(original_file_name)
            self.__command_arguments[index_in_args] = new_input_files[\
                original_file_name]
            
    def has_distributable_start_step(self):
        """Return true if there is at least one input file whose
        compilation process can be distributed.
        This is used to make the following command :
        gcc -c test.c foo.c bar.o
        compile remotely.
        If is_distributable used get_start_step() to know wether the command
        is distributable or not, this command would be compiled locally."""
        for (index, file) in self.get_input_files():
            if get_start_step_of_file(file) < 4:
                return 1
        return 0
    
    def get_output_files(self):
        """Return a tuple containing the filename of every files that
        the command execution will output.
        FIXME: We might handle the -ftest-coverage style options later,
        because those options create files. It would be usefull to know wich
        are those files."""

        if "-o" in self.__command_arguments:
            # the output file has been explicitly given
            # The gcc info page say that if -o is given,
            # _only one_ file can be output
            i = 0
            for arg in self.__command_arguments:
                if arg == "-o":
                    last_index_output_switch = i
                i = i + 1
            try:
                return (self.__command_arguments[last_index_output_switch + 1],)
            except IndexError:
                # FIXME: handle this case better.
                # Raise some exception or whatever
                return ("",)
        elif self.get_stop_step() < 4:
            # the output file was not given explcitly,
            # and the command will not produce an executable, so
            # each input file will be output with a name depending on the
            # last step of the compilation
            res = []
            for (index, file) in self.get_input_files():
                file_output_name = self.get_output_file_name_for_step(\
                    file,\
                    self.get_stop_step())
                # sometimes, wrong commands as the following :
                # gcc -c test.c foo.c bar.o
                # can cause gcc not to process bar.o, because
                # we ask it not to go beyond compilation step, and
                # to process an already compiled file.
                # So this file won't be part of the compilation process, no
                # output will be generated for it
                if file_output_name != "":
                    res.append(file_output_name)
            return tuple(res)
        else:
            # no output file explicitly given, and
            # the compilation must go through all steps.
            # So it will end by producing a "a.out" file
            return ("a.out",)

    def get_options(self):
        """This method returns the tuple of the options
        like "-fstrict-prototypes", "-O3" etc ...
        """
        if self.__options != None:
            return self.__options
        self.__options = []
        for arg in self.__command_arguments:
            if arg[0] == '-' :
                self.__options.append(arg)
        return tuple(self.__options)

    def do_preprocessing_step(self):
        """Return one tuple of tuples that  match filename
        as in the original command line with a temporary file
        object used to hold the preprocessed data.
        For example, the following command line :
        gcc -c test.c foo.i bar.S baz.s
        will return :
        ((temp_file_object, "test.cc"),
        (foo.i_file_object, "foo.i"),
        (temp_file_object, "bar.S"),
        (baz.s_file_object, "baz.s")
        )
        If one of the preprocessing step exit with an error code != 0,
        we exit with the same exit code and delete the temporary files created
        so far.
        """
        files = []
        stop_step = self.get_stop_step()
        options = get_preprocessing_options(self.get_options())
        for file in self.get_input_files():
            if get_start_step_of_file(file[1]) == 1:
                # We need to preprocess this file
                tmp_file = tempfile.TemporaryFile()
                if __debug__:
                    syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, 
                                  "Preprocessing : " + \
                                  self.get_local_compiler_path() + " -E " + \
                                  " ".join(get_preprocessing_options(self.get_options()))\
                                  + " " + file[1])
                preprocess_out = os.popen(self.get_local_compiler_path() + " -E " + \
                                          " ".join(\
                    get_preprocessing_options(self.get_options()))\
                                          + " " + file[1])
                data = preprocess_out.read()
                tmp_file.write(data)
                tmp_file.flush()
                files.append((tmp_file, file[1]))
                exit_code = preprocess_out.close()
                if exit_code != None:
                    sys.exit(exit_code)
            else:
                # we don't need to preprocess this file
                # if the file is not processed, just append
                # a None reference to it so that it's data won't be sent,
                # but the remote compiler we'll create one file locally
                # to keep gcc happy and not complaining about a missing file
                if get_start_step_of_file(file[1]) > stop_step:
                    files.append((None, file[1]))
                else:
                    try:
                        files.append((open(file[1]), file[1]))
                    except IOError:
                        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON,\
                                      "DMS: can't open file : "\
                                      + file[1] + "! It might be an error.")
                        # a file does not exist, so invoke gcc to
                        # report the error correctly and exit with
                        # the same error code
                        sys.exit(os.system(" ".self.get_command_args()))
        return tuple(files)
            
    def get_local_compiler_path(self):
        if self.__local_compiler_path == None:

            keys_match = [
                ("CXX_PATH", "compiler_path", "CXX_PATH")
                ]

            command_line_match=[]
            
            default_values = {
                "CXX_PATH" : commands.getoutput("which c++")
                }
            
            config_file_path = "/etc/dms.cfg"
            
            #FIXME Catch the exception
            self.__local_compiler_path = Configuration.get_configuration(self.display_usage,
                                                                         self.check_values,
                                                                         keys_match,
                                                                         default_values,
                                                                         command_line_match,
                                                                         config_file_path,
                                                                         0)["CXX_PATH"]
        return self.__local_compiler_path

    def display_usage(self):
        print "WARNING, You shouldn't be reading this text ..."

    def check_values(self, config_values):
        #FIXME Check that the compiler exists
        return ((), 1)
