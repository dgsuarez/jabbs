import unittest
import threading
from jabbs.testing import clienttester


class TestCounter(unittest.TestCase):

    def test_counter_conversation(self):
        """test concurrent access"""
        c1 = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("next", "1"),
                                 ("next", "2"),
                                 ("next", "3"),
                                 ("next", "4"),
                                 ("next", "5"),
                                 ("bye", "bye")])
        c2 = clienttester.Tester("curris@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("next", "1"),
                                 ("next", "2"),
                                 ("next", "3"),
                                 ("next", "4"),
                                 ("next", "5"),
                                 ("bye", "bye")])
        t1 = TestThread(c1)
        t2 = TestThread(c2)
        t1.start()
        t2.start()
        while (t1.isAlive() and t2.isAlive()):
            pass
        self.assertEquals([], t1.result)
        self.assertEquals([], t2.result)


class TestThread(threading.Thread):
    
    def __init__(self, tester):
        self.tester = tester
        threading.Thread.__init__(self)
        
    def run(self):
        self.result = self.tester.start()
        
if __name__ == "__main__":
    unittest.main()