import unittest

from jabbs.configparser import Config

class DummyControl:
    def user_control(self, user):
        return "good"

class TestParser(unittest.TestCase):
    
    def test_parse_file(self):
        cfg = Config("configparser.cfg")
        self.assertEquals(cfg.jid,"botiboti@127.0.0.1")
        self.assertEquals(cfg.password,"b3rb3r3ch0")
        self.assertEquals(cfg.starter, DummyControl)
        self.assertEquals(cfg.starter_params, {"one": "yes", "two": "no"})
        self.assertEquals(cfg.user_control(""), "good")
        self.assertEquals(cfg.nick,"botiboti")
        self.assertEquals(cfg.rooms_to_join,["chat@conference.127.0.0.1","chats@conference.127.0.0.1"])
        

if __name__ == "__main__":
    unittest.main()