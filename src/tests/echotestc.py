import unittest
from jabbs.testing import clienttester


class TestEcho(unittest.TestCase):

    def test_echo_conversation(self):
        """test a simple echo bot"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hola", "hola"),("adios", "adios")])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()