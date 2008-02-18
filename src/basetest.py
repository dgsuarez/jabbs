import unittest
import re
import jabbs as base

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def setUp(self):
        self.bot = base.Core("botiboti@127.0.0.1", "b3rb3r3ch0")

    def test_jid(self):
        """Test creation of the bot"""
        self.assertEqual(self.bot.jid, JID("botiboti", "127.0.0.1", "Core"))


    def test_controller_from_bot_methods(self):
        """Test bot_ methods"""
        sb=self.SampleBotMethod("", "")
        self.assertEqual(base.controller_from_bot_methods(sb).sort(),
                         [("^bye.*", sb.bot_bye),("^hello.*", sb.bot_hello)].sort())

    def test_event(self):
        """Test events actually get called"""
        def call_me_twice(bot):
            if not "dangerous_variable" in dir(bot):
                bot.dangerous_variable = 0
            bot.dangerous_variable += 1
            if bot.dangerous_variable == 2:
                bot.disconnect()
                self.assertTrue(True)
        bot = base.Core("botiboti@127.0.0.1", "b3rb3r3ch0")
        bot.add_event(base.Event(call_me_twice, 1, 0, {"bot": bot}))
        bot.start()

    class SampleBotMethod(base.Core):
        def bot_hello(self, message):
            return "hi"
        def bot_bye(self, message):
            return "bye"

    def test_add_event(self):
        """Test add events"""
        self.bot.add_event(base.Event(self.test_add_event, 0))
        self.assertEqual(self.bot._Core__events[0].fun, self.test_add_event)
        self.assertEqual(self.bot._Core__events[0].elapsed, 0) 
        self.assertEqual(self.bot._Core__events[0].timeout, 0)


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()
