import unittest
import re
import base

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def setUp(self):
        self.bot = base.BaseBot("botiboti@127.0.0.1", "b3rb3r3ch0")

    def test_jid(self):
        self.assertEqual(self.bot.jid, JID("botiboti", "127.0.0.1", "BaseBot"))

    def test_default(self):
        self.assertEqual(self.bot.default(Message(body="hola")),
                Message(body="hola"))

    def test_get_reply_stanza_inverted(self):
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_stanza(m, lambda x:Message(body=x.get_body()[::-1]))
        self.assertEqual(r.get_body(), "aloh")

    def test_get_reply_stanza_regular(self):
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_stanza(m, lambda x:x)
        self.assertEqual(r.get_body(), "hola")

    def test_controller_from_bot_methods(self):
        sb=self.SampleBotMethod("", "")
        self.assertEqual(sb.controller_from_bot_methods().sort(),
                         [("^bye.*", sb.bot_bye),("^hello.*", sb.bot_hello)].sort())

    class SampleBotMethod(base.BaseBot):
        def bot_hello(self, message):
            return "hi"
        def bot_bye(self, message):
            return "bye"


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()
