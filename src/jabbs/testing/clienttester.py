import re

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

class Tester(JabberClient):
    """Has a dialogue with a bot through Jabber

    """
    
    def __init__(self, jid, passwd,to_jid, message_list):
        """message_list is a list of tuples of strings, each tuple is a 
        sentence and it's expected reply

        """
        self.messages = message_list
        self.to_jid = JID(to_jid)
        jid_ = JID(jid)
        self.fail_count = 0
        if not jid_.resource:
            jid_ = JID(jid_.node, jid_.domain, "Mibot")
        JabberClient.__init__(self, jid_, passwd)
        self.send_next = True
        self.failed_messages = []

    def start(self):
        """Starts the conversation. Returns True if every answer was right,
        else returns False
        
        """
        self.connect()
        self.loop()
        return self.failed_messages

    def session_started(self):
        JabberClient.session_started(self)
        self.stream.set_message_handler("normal", self.received)
    
    def received(self, stanza):
        if not stanza.get_body():
            return 
        self.send_next = True
        if not "expected" in dir(self):
            return
        if not re.compile(self.expected).search(stanza.get_body()):
            self.fail_count += 1
            self.failed_messages.append((self.expected, stanza.get_body()))

    def send(self, message, jid):
        m = Message(to_jid=jid, body=message, stanza_type="chat")
        self.stream.send(m)

    def loop(self, timeout=1):
         while 1:
            stream = self.get_stream()
            if not stream:
                break
            act = stream.loop_iter(timeout)
            if not act:
                if self.send_next:
                    try:
                        m, self.expected = self.messages.pop(0)
                    except:
                        self.disconnect()
                        return
                    self.send(m, self.to_jid)
                    if self.expected:
                        self.send_next = False
                self.idle()