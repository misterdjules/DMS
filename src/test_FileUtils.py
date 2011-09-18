"""Unit testing for the FileUtils module"""

__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "8 August 2002"

import unittest
import FileUtils

class FileUtilsTest(unittest.TestCase):
    """Test every function of the FileUtils module"""

    def testGetFileExtension(self):
        files = (
            ("test.c", ".c"),
            ("test.o", ".o"),
            ("test.s", ".s"),
            ("test.S", ".S"),
            ("test.i", ".i"),
            ("test.ii", ".ii"),
            ("test", ""),
            ("test.c.o", ".o"),
            (".test.c", ".c"),
            ("../../../../.test.c", ".c"),
            ("./.test.c.c", ".c"),
            ("../../test.o.c.ii", ".ii")
            )
        for file in files:
            self.assertEqual(FileUtils.get_file_extension(file[0]), file[1])

    def testStripFileExtension(self):
        files =    (
            ("test.c", "test"),
            ("test.o", "test"),
            ("test.s", "test"),
            ("test.S", "test"),
            ("test.i", "test"),
            ("test.ii", "test"),
            ("test", "test"),
            ("test.c.o", "test.c"),
            (".test.c", ".test"),
            ("../../../../.test.c", "../../../../.test"),
            ("./.test.c.c", "./.test.c"),
            ("../../test.o.c.ii", "../../test.o.c")
            )
        for file in files:
            self.assertEqual(FileUtils.strip_file_extension(file[0]), file[1])
            
if __name__ == "__main__":
    unittest.main()
