import unittest
from jabbs.testing import clienttester


class TestJablog(unittest.TestCase):

    def test_log(self):
        """test jablog"""
        c1 = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hola", None),
                                 ("end_logging", None)])
        c2 = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("adios", None),
                                 ("end_logging", None)])
        c1.start()
        f = open("gramparsons@127.0.0.1_log.txt", "r")
        log = f.read()
        self.assertEquals("<gramparsons@127.0.0.1/Mibot> hola\n---------------------------------\n\n", log)
        f.close()
        c2.start()
        f = open("gramparsons@127.0.0.1_log.txt", "r")
        log = f.read()
        self.assertEquals("<gramparsons@127.0.0.1/Mibot> hola\n---------------------------------\n\n<gramparsons@127.0.0.1/Mibot> adios\n---------------------------------\n\n", log)
        print log


if __name__ == "__main__":
    unittest.main()
