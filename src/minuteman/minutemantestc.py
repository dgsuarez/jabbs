import unittest
from jabbs.testing import clienttester


class TestBase(unittest.TestCase):

    def test_minutes(self):
        """Tests adding a scribe, new minutes, etc"""
        conversation = [("hola", None),
                        ("Chair: Diego", "Only the scribe can set the chair. If you havent, set a scribe"),
                        ("I'm the scribe", "Scribe set to: Mibot"),
                        ("I'm the scribe", "Scribe is already set"),
                        ("Chair: Diego", "Chair is: Diego"),
                        ("Title: Las cosas que te cuento", "Title is: Las cosas que te cuento"),
                        ("To be minuted: Pepe: hola","Before submiting a minute you must submit a topic"),
                        ("Topic: Prueba", "Topic is: Prueba"),
                        ("To be minuted: Pepe: hola",None),
                        ("... y adios", None),
                        ("End minutes", "Minutes ended")
                        ]
        c = clienttester.Tester("gramparsons@127.0.0.1", 
                                "b3rb3r3ch0", 
                                "botiboti@127.0.0.1", 
                                conversation)
        self.assertTrue(c.start())



suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()