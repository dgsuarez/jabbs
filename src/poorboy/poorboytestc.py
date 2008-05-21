import unittest
from jabbs.testing import clienttester


class TestPoorboy(unittest.TestCase):

    def test_poorboy_conversation(self):
        """test a conversation with poorboy"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("You are a machine", "There's no way you can get away with calling me a machine"),
                                 ("I remember France", "I don't recall France, tell me more about it"),
                                 ("I am sad because of the weather", "Are you sad often?"),
                                 ("glu", "I can't grasp what you are saying"),
                                 ("glu", "Come on, let's change subjects"),
                                 ("glu", "I don't know what you mean")])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()