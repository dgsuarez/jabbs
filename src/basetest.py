import unittest
import re
import base

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def setUp(self):
        self.bot = base.Core("botiboti@127.0.0.1", "b3rb3r3ch0")

    def test_jid(self):
        """Test creation of the bot"""
        self.assertEqual(self.bot.jid, JID("botiboti", "127.0.0.1", "Core"))

    def test_get_reply_stanza(self):
        """Test replies to different kind of messages"""
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_stanza(m, lambda x:Message(body=x.get_body()[::-1]))
        self.assertEqual(r.get_body(), "aloh")
        m=Message(from_jid=JID("c@s.com"),body="hola")
        r=self.bot.get_reply_stanza(m, lambda x:x)
        self.assertEqual(r.get_body(), "hola")

    def test_controller_from_bot_methods(self):
        """Test bot_ methods"""
        sb=self.SampleBotMethod("", "")
        self.assertEqual(base.controller_from_bot_methods(sb).sort(),
                         [("^bye.*", sb.bot_bye),("^hello.*", sb.bot_hello)].sort())

    class SampleBotMethod(base.Core):
        def bot_hello(self, message):
            return "hi"
        def bot_bye(self, message):
            return "bye"

    def test_add_event(self):
        """Test add events"""
        self.bot.add_event(self.test_add_event, 0)
        self.assertEqual(self.bot._Core__events[0].fun, self.test_add_event)
        self.assertEqual(self.bot._Core__events[0].elapsed, 0) 
        self.assertEqual(self.bot._Core__events[0].timeout, 0)


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()
