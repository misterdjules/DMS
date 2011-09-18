"""CompilerCommand class unit tests"""

__author__ = "Julien Barbot <julien-barbot@laposte.net>\
and Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "8 August 2002"

import unittest
import CompilerCommand_c

class CompilerCommandTest(unittest.TestCase):
    
    def testIsDistributable(self):
        """is_distributable() method should give the good result"""
        commands = (
            ("gcc -c test.c", True),
            ("gcc -c test.c -o test.o", True),
            ("gcc test.c -o test", False),
            ("gcc -g -O2 -W -Wall -Wshadow -Wpointer-arith \
            -Wcast-align -c -o distcc.o distcc.c", True),
            ("gcc -o distcc distcc.o clinet.o where.o\
            hosts.o trace.o util.o io.o exec.o arg.o rpc.o\
            tempfile.o bulk.o help.o filename.o -lpopt", False),
            ("gcc -DHAVE_CONFIG_H -I. -I. -I../include \
            -DPREFIX=\"/usr\" -g -O2 -Wall -c buildmark.c", True),
            ("gcc -DPREFIX=\"/usr\" -g -O2 -Wall   \
            -o micq  conv.o conv_rus.o conv_jp.o file_util.o \
            icq_response.o micq.o server.o util.o util_ui.o \
            mreadline.o mselect.o network.o msg_queue.o tabs.o \
            i18n.o util_table.o contact.o tcp.o packet.o \
            cmd_pkt_cmd_v5.o cmd_pkt_cmd_v5_util.o cmd_pkt_server.o \
            cmd_user.o preferences.o util_io.o session.o cmd_pkt_v8.o \
            cmd_pkt_v8_flap.o cmd_pkt_v8_tlv.o cmd_pkt_v8_snac.o \
            buildmark.o", False),
            ("gcc -DHAVE_CONFIG_H -I. -I. -I../include    -DPREFIX=\"/usr\" \
            -g -O2 -Wall -c conv.c", True),
            ("gcc -D__KERNEL__ -I/usr/src/linux-2.4.18-xfs/include  -Wall \
            -Wstrict-prototypes -Wno-trigraphs -O2 -fno-strict-aliasing -fno-common \
            -fomit-frame-pointer -pipe -mpreferred-stack-boundary=2 -march=i686\
            -DKBUILD_BASENAME=main -c -o init/main.o init/main.c", True),
            ("gcc -D__KERNEL__ -I/usr/src/linux-2.4.18-xfs/include  -Wall \
            -Wstrict-prototypes -Wno-trigraphs -O2 -fno-strict-aliasing -fno-common \
            -fomit-frame-pointer -pipe -mpreferred-stack-boundary=2 -march=i686 \
            -DKBUILD_BASENAME=exec_domain  -DEXPORT_SYMTAB -c exec_domain.c", True),
            # more complex tests
            # there is a trailing -E switch, so preprocess locally
            ("gcc -c test.c -o test.o -E", False),
            ("gcc test.c", False),
            ("gcc -M test.c", False),
            ("gcc -MG test.c", False),
            ("gcc -c test.c -o test.o -MG", False),
            ("gcc -D__KERNEL__ -I/usr/src/linux-2.4.18-xfs/include  -Wall \
            -Wstrict-prototypes -Wno-trigraphs -O2 -fno-strict-aliasing -fno-common \
            -fomit-frame-pointer -pipe -mpreferred-stack-boundary=2 -march=i686 \
            -DKBUILD_BASENAME=exec_domain  -MMD -DEXPORT_SYMTAB -c exec_domain.c", False),
            ("gcc -D__KERNEL__ -I/usr/src/linux-2.4.18-xfs/include  -Wall \
            -Wstrict-prototypes -Wno-trigraphs -O2 -fno-strict-aliasing -fno-common \
            -fomit-frame-pointer -pipe -mpreferred-stack-boundary=2 -march=i686 \
            -DKBUILD_BASENAME=exec_domain  -fprofile-arcs -DEXPORT_SYMTAB -c exec_domain.c", False),
            # Not distributable because there is the -ftest-coverage
            ("gcc -DHAVE_CONFIG_H -I. -ftest-coverage -I. -I../include    -DPREFIX=\"/usr\" \
            -g -O2 -Wall -c conv.c", False),
            ("gcc -c -o truc.o -S -E test.c", False),
            ("gcc -c test.i foo.c -o bar.o", True)
            )
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(result, compiler_command.is_distributable())

    def testGetInputFilesTest(self):
        """test the get_input_files() method"""
        commands = (
            ("gcc -DHAVE_CONFIG_H -I. -ftest-coverage -I. -I../include\
            -DPREFIX=\"/usr\"  -g -O2 -Wall -c conv.c", ((11, "conv.c"),)),
            ("gcc -DPREFIX=\"/usr\" -g -O2 -Wall   -o micq  \
            conv.o conv_rus.o conv_jp.o file_util.o icq_response.o",
             ((7, "conv.o"),
              (8, "conv_rus.o"),
              (9, "conv_jp.o"),
              (10, "file_util.o"),
              (11, "icq_response.o"))),
            ("gcc -E test.c -M -o test.i", ((2, "test.c"),)),
            ("gcc -E test.c -M -o test.i", ((2, "test.c"),)),
            ("gcc -c test.c", ((2, "test.c"),))
            )
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(result, compiler_command.get_input_files())
        
    def testGetStartStep(self):
        """Test the get_start_step() method"""
        commands = (
            ("gcc -c test.c", 1),
            ("gcc -S test.S", 1),
            ("gcc -c test.S", 1),
            ("gcc -c test.i", 2),
            ("gcc -c test.s", 3),
            ("gcc -E test.c -o test.s", 1),
            ("gcc -E test.c test.o -o test.s", 4),
            ("gcc test.o foo.o baz.o", 4),
            ("gcc test.o bar.o test.c test.S test.s", 4)
            )
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(result, compiler_command.get_start_step())

    def testGetStopTest(self):
        commands = (
            # basic tests
            ("gcc -E test.c", 1),
            ("gcc -M test.c", 1),
            ("gcc -MM test.c", 1),
            ("gcc -MF test.c", 1),
            ("gcc -MG test.c", 1),
            ("gcc -MP test.c", 1),
            ("gcc -MT test.c", 1),
            ("gcc -MQ test.c", 1),
            ("gcc -MD test.c", 1),
            ("gcc -MMD test.c", 1),
            ("gcc -c test.c", 3),
            ("gcc -S test.c", 2),
            # more complex ones
            ("gcc -S -c -E -M test.c", 1),
            ("gcc -S -c test.c", 2),
            )
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(result, compiler_command.get_stop_step())

    def testGetOutputFileNameForStep(self):
        files = (
            ("test.c", 3, "test.o"),
            ("test.c", 1, "test.i"),
            ("test.c", 2, "test.s"),
            ("test.i", 3, "test.o"),
            ("test.S", 3, "test.o"),
            ("test.S", 1, "test.i"),
            ("test.S", 2, "test.s"),
            ("test.s", 3, "test.o"),
            ("test.o", 1, ""),
            ("test.o", 2, ""),
            ("test.o", 3, ""),
            ("test.s", 1, ""),
            ("test.s", 2, ""),
            ("test.k", 1, ""),
            ("test.k", 2, ""),
            ("test.k", 3, ""),
            ("test", 1, ""),
            ("test", 2, ""),
            ("test", 3, ""),
            ("test.i", 1, ""),
            ("test.i", 2, "test.s"),
            ("test.o", 2, ""),
            ("test.s", 1, "")
            )
        for file in files:
            self.assertEqual(CompilerCommand.get_output_file_name_for_step(file[0],
                                                                           file[1]),
                             file[2])
            
    def testGetOutpurFiles(self):
        """Test the get_output_files() method"""
        commands = (
            ("gcc -g -O2 -W -Wall -Wshadow -Wpointer-arith -Wcast-align\
            -c -o distcc.o distcc.c", ("distcc.o",)),
            ("gcc  -o distcc distcc.o clinet.o where.o hosts.o trace.o util.o\
            io.o exec.o arg.o rpc.o tempfile.o bulk.o help.o filename.o -lpopt",
             ("distcc",)),
            ("gcc -c test.c", ("test.o",)),
            ("gcc -c test.c foo.c bar.c baz.c", ("test.o", "foo.o", "bar.o", "baz.o")),
            ("gcc -c test.c foo.S stuff.s bar.i baz.o",
             ("test.o", "foo.o", "stuff.o", "bar.o")),
            ("gcc -g -O2 -W -Wall -Wshadow -Wpointer-arith -Wcast-align\
            -c -o distcc.o distcc.c -o distcc2.o", ("distcc2.o",)),
            ("gcc -c test.c -S -c", ("test.s",))
            )
        
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(compiler_command.get_output_files(), result)


    def testGetOptions(self):
        commands = (
            ("gcc test.c", ()),
            ("gcc -c test.c", ("-c",)),                              
            ("gcc -c test.c -o toto", ("-c", "-o"))
            )
        for (cmd, res) in commands:
            compiler_command = CompilerCommand.CompilerCommand(cmd.split())
            self.assertEqual(compiler_command.get_options(), res)
            
    def testGetPreprocessingOptions(self):
        """Test the get_preprocessing_options() function"""
        commands = (
            ("gcc test.c", ()),
            ("gcc -c test.c", ()),                              
            ("gcc -c test.c -o toto", ()),
            ("gcc -c -I../../include test.c -o toto", ("-I../../include",)),
            ("gcc -DNDEBUG -c -I../../include test.c -o toto",
             ("-DNDEBUG", "-I../../include",)),
            ("gcc -D__KERNEL__ -I/usr/src/linux-2.4.18-xfs/include  -Wall \
            -Wstrict-prototypes -Wno-trigraphs -O2 -fno-strict-aliasing -fno-common \
            -fomit-frame-pointer -pipe -mpreferred-stack-boundary=2 -march=i686\
            -DKBUILD_BASENAME=main -c -o init/main.o init/main.c",
             ("-D__KERNEL__", "-I/usr/src/linux-2.4.18-xfs/include",  "-Wall", \
              "-Wstrict-prototypes", "-Wno-trigraphs", "-O2",\
              "-fno-strict-aliasing", "-fno-common", \
              "-fomit-frame-pointer", "-pipe", "-mpreferred-stack-boundary=2", \
              "-march=i686", "-DKBUILD_BASENAME=main"))
            )
        for (command, result) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            self.assertEqual(CompilerCommand.get_preprocessing_options(\
                compiler_command.get_options()), result)

    def testDoPreprocessingStep(self):
        """Test the do_preprocessing_step() method"""
        commands = (
            ("gcc -c test.c", ("test.c",)),
            ("gcc -c gtk2.c -o gtk2.o -I/usr/include/gtk-1.2\
            -I/usr/include/glib-1.2 -I/usr/lib/glib/include \
            -I/usr/X11R6/include", ("gtk2.c",)),
            ("gcc -c gtk2.c gtk3.c gtk4.c gtk1.c -o gtk2.o -I/usr/include/gtk-1.2\
            -I/usr/include/glib-1.2 -I/usr/lib/glib/include \
            -I/usr/X11R6/include", ("gtk2.c", "gtk3.c", "gtk4.c", "gtk1.c"))
            )
        for (command, orig_file_names) in commands:
            compiler_command = CompilerCommand.CompilerCommand(command.split())
            result = compiler_command.do_preprocessing_step()
            result_orig_file_names = []
            for (tmp_file, orig_file_name) in result:
                result_orig_file_names.append(orig_file_name)
            self.assertEqual(tuple(result_orig_file_names), orig_file_names)
            
if __name__ == "__main__":
    unittest.main()
