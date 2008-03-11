import unittest
from jabbs.testing import clienttester


class TestBase(unittest.TestCase):

    def test_transference(self):
        """Tests transference from one controller to another"""
        c = clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hola pepe", "hi"),("adios", "bye pepe"),("hola", "hola"), ("adios pepe", "adios pepe")])
        self.assertTrue(c.start())


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()