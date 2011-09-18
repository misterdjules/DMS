"""Unit testing of the ListUtils module"""

__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "8 August 2002"

import unittest
import ListUtils

class ListUtilsTest(unittest.TestCase):
    """Test every function of the ListUtils module"""

    def testGetIntersection(self):
        """Test if the list intersection method works"""
        lists = (
            ([], [], []),
            ([], [1, 2], []),
            ([1], [1, 2],[1]),
            ([1], [2], []),
            ([1, 4], [2, 3], []),
            ([1, 2], [1, 2], [1, 2])
            )
        for list in lists:
            self.assertEqual(ListUtils.get_intersection(list[0], list[1]),
                             list[2])
            self.assertEqual(ListUtils.get_intersection(list[1], list[0]),
                             list[2])

if __name__ == "__main__":
    unittest.main()

