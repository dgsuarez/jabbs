import unittest
import threading
from jabbs.testing import clienttester


class TestCounter(unittest.TestCase):

    def test_counter_conversation(self):
        """test concurrent access"""

        c1 = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1",
                                [("next1", "1"),
                                 ("next2", "2"),
                                 ("next3", "3"),
                                 ("next4", "4"),
                                 ("next5", "5"),
                                 ("bye", "bye")] 
                                )
        c2 = clienttester.Tester("curris@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("next1", "1"),
                                 ("next2", "2"),
                                 ("next3", "3"),
                                 ("next4", "4"),
                                 ("next5", "5"),
                                 ("bye", "bye")])
        t1 = TestThread(c1)
        t2 = TestThread(c2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
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