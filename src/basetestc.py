import unittest
import base
import clienttester

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def test_echo_conversation(self):
        c=clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hola", "hola"),("adios", "adios")])
        self.assertTrue(c.start())

    def test_check_events(self):
        c=clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [(None, "hi")])
        self.assertTrue(c.start())


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()


