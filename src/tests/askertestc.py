import unittest
from jabbs.testing import clienttester


class TestAsker(unittest.TestCase):

    def test_asking_conversation(self):
        """test a simple echo bot"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("regular", "Is it correct?"),
                                 ("yes", "good"),
                                 ("yesno", "Is it correct?"),
                                 ("yes", "good"),
                                 ("choice","Is it correct?"),
                                 ("1", "good")
                                 ])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()