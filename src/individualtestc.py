import clienttester
import individual
import unittest

class TestIndividual(unittest.TestCase):
    def test_create_message(self):
        """individual always replies with hola"""
        c=clienttester.Tester("gramparsons@127.0.0.1", "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                [("hiola", "hola"),("adios", "hola")])
        self.assertTrue(c.start())


suite = unittest.TestLoader().loadTestsFromTestCase(TestIndividual)
if __name__ == "__main__":
    unittest.main()
