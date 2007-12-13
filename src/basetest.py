import unittest
import base

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def setUp(self):
        self.bot = base.BaseBot("botiboti@127.0.0.1", "b3rb3r3ch0")

    def test_jid(self):
        self.assertEqual(self.bot.jid, JID("botiboti", "127.0.0.1", "BaseBot"))

    def test_default(self):
        self.assertEqual(self.bot.default("hola"), "hola")

    def test_get_reply_message_inverted(self):
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_message(m, lambda x:x[::-1])
        self.assertEqual(r.get_body(), "aloh")

    def test_get_reply_message_regular(self):
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_message(m, lambda x:x)
        self.assertEqual(r.get_body(), "hola")

    def test_get_reply_message_jid(self):
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_message(m, lambda x:x)
        self.assertEqual(r.get_to(), m.get_from())




suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()
