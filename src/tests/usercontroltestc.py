import unittest
from jabbs.testing import clienttester


class TestUserControl(unittest.TestCase):

    def test_user_control(self):
        """test user access"""
        c1 = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hi", "good")])
        
        c2 = clienttester.Tester("curris@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hi", "You are not allowed to talk with me")])
        self.assertEquals([], c1.start())
        self.assertEquals([], c2.start())



if __name__ == "__main__":
    unittest.main()