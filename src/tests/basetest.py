import unittest
import re
import jabbs.core as base
from jabbs import controller

from pyxmpp.all import JID, Message

class TestBase(unittest.TestCase):

    def setUp(self):
        self.bot = base.Core("botiboti@127.0.0.1", "b3rb3r3ch0", controller.Controller)

    def test_jid(self):
        """Test creation of the bot"""
        self.assertEqual(self.bot.jid, JID("botiboti", "127.0.0.1", "Core"))


    def test_controller_from_bot_methods(self):
        """Test bot_ methods"""
        sb = self.SampleBotMethod()
        self.assertEqual(base.controller_from_bot_methods(sb).sort(),
                         [("^bye.*", sb.bot_bye),("^hello.*", sb.bot_hello)].sort())

    class SampleBotMethod(controller.Controller):
        def bot_hello(self, message):
            return "hi"
        def bot_bye(self, message):
            return "bye"



suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
if __name__ == "__main__":
    unittest.main()