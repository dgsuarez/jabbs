import unittest
from jabbs.testing import clienttester


class TestAsker(unittest.TestCase):

    def test_asking_conversation(self):
        """Test ask system with yes/no, regular and multiple choice
        questions
        
        """
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("regular", "Is it correct?"),
                                 ("yes", "good"),
                                 ("yesno", "Is it correct?"),
                                 ("nana", "Please answer yes or no"),
                                 ("yes", "good"),
                                 ("choice","Is it correct?"),
                                 ("4", "You must input a valid option"),
                                 ("1", "good")
                                 ])
        self.assertEquals([], c.start())



if __name__ == "__main__":
    unittest.main()