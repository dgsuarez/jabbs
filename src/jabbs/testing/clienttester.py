from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

class Dialogue:
    """Implements a dialogue in the form of pairs of sentences. The
    second sentence in the pair is a reply for the first one

    """
    def __init__(self, message_list):
        """message_list is a list of tuples of strings, each tuple is a 
        sentence and it's reply

        """
        self.__message_list = message_list
        self.index=0

    def get_next_message(self):
        """If there are messages left in the dialogue returns the
        next. Else returns None

        """
        if self.index == len(self.__message_list):
            return None
        return self.__message_list[self.index][0]

    def get_answer(self):
        """If there are messages left in the dialogue returns the
        next. Else returns None

        """
        if self.index == len(self.__message_list):
            return None
        self.index = self.index+1
        return self.__message_list[self.index-1][1]


class Tester(JabberClient):
    """Has a dialogue with a bot through Jabber

    """
    
    def __init__(self, jid, passwd,to_jid, message_list):
        """message_list is a list of tuples of strings, each tuple is a 
        sentence and it's expected reply

        """
        self.messages = Dialogue(message_list)
        self.to_jid = JID(to_jid)
        jid_ = JID(jid)
        self.fail_count = 0
        if not jid_.resource:
            jid_ = JID(jid_.node, jid_.domain, "Mibot")
        JabberClient.__init__(self, jid_, passwd)
        self.send_next = True

    def start(self):
        """Starts the conversation. Returns True if every answer was right,
        else returns False
        
        """
        self.connect()
        self.loop()
        return self.fail_count == 0

    def session_started(self):
        JabberClient.session_started(self)
        self.stream.set_message_handler("normal", self.received)
    
    def received(self, stanza):
        if not stanza.get_body():
            return 
        self.send_next = True
        if stanza.get_body() != self.messages.get_answer():
            self.fail_count += 1

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
                    m = self.messages.get_next_message()
                    if not m:
                        self.disconnect()
                    self.send(m, self.to_jid)
                    self.send_next = False
                self.idle()