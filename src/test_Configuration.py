__author__ = "Julien Gilli <jgilli@nerim.fr>,\
Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "21 August 2002"

import unittest
import Configuration

class test_Configuration(unittest.TestCase):
    def testUserIsInGroup(self):
        """Test the user_is_in_group function."""
        users = (
            ("root", "root", 1),
            ("bin", "bin", 1),
            ("daemon", "daemon", 1),
            ("daemon", "users", 0)
            )

        for user in users:
            self.assertEqual(Configuration.user_is_in_group(user[0], \
                                                            user[1]),\
                             user[2])

    def testGetConfiguration(self):
        """Test the get_configuration function."""
        cfgs = (
            ("../tests/test1.cfg", 0),
            ("../tests/test2.cfg", 0),
            ("../tests/test3.cfg", 0),
            ("../tests/test4.cfg", 1)
            )
        for (cfg_file, result) in cfgs:
            print "Testing file : " + cfg_file
            config = Configuration.get_configuration(cfg_file)
            self.assertEqual(Configuration.check_values(config), result)
            
        
if __name__ == "__main__":
    unittest.main()
