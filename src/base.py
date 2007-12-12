import re

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient


class BaseBot(JabberClient):

    def __init__(self, jid, passwd):
        """Initializes the bot with jid (username@jabberserver) and it's
        password

        """
        jid_ = JID(jid)
        if not jid_.resource:
            jid_=JID(jid_.node, jid_.domain, self.__class__.__name__)
        JabberClient.__init__(self, jid_, passwd)

    def session_started(self):
        """Triggered when the session starts. Sets some event handlers
        
        """
        JabberClient.session_started(self)
        self.stream.set_message_handler("normal", self.received)

    def controller(self):
        """Default controller implementation. Should be overriden in
        derived classes.
            It returns a list of the form [(regex, method), ...] 
        received messages will be matched against the regexs and method
        will be called in the first one that matches
        
        """
        return [(r".*", self.default)]

    def received(self, stanza):
        """Handler for normal messages. 

        """
        if not stanza.get_body():
            return
        for pat, fun in self.controller():
            if re.compile(pat).match(stanza.get_body()):
                self.send(self.get_reply_message(stanza, fun))
                return

    def default(self, message):
        """Sample default response, acts as an echo bot
            Should be overrriden in derived classes

        """
        return message
    
    def send(self, stanza):
        """Replies to a stanza"""
        self.stream.send(stanza)

    def get_reply_message(self, stanza, fun):
        """Gets a reply to a stanza from aplying fun to
        the stanza's body

        """
        return Message(to_jid=stanza.get_from(), 
                       body=fun(stanza.get_body()))

    def start(self):
        """Connects to the server and starts waiting for input"""
        self.connect()
        self.loop()


if __name__ == "__main__":
    BaseBot("botiboti@127.0.0.1", "b3rb3r3ch0").start()
