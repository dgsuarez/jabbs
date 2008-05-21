import unittest
from jabbs.testing import clienttester


class TestJabanswer(unittest.TestCase):

    def test_jabanswer(self):
        """test a question in jabanswer"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("why is the sky blue?", ".+")])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()