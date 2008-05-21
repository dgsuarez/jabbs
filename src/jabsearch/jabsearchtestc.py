import unittest
from jabbs.testing import clienttester


class TestJabsearch(unittest.TestCase):

    def test_jabsearch(self):
        """test a search in jabsearch"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("jabsearch hola", ".+")])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()