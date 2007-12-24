import re

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient


class BaseBot(JabberClient):

    def __init__(self, jid, passwd):
        """Initializes the bot with jid (username@jabberserver) and it's
        password

        """
        self.__time_elapsed=0
        self.__events=[]
        jid_ = JID(jid)
        if not jid_.resource:
            jid_=JID(jid_.node, jid_.domain, self.__class__.__name__)
        JabberClient.__init__(self, jid_, passwd)

    def session_started(self):
        """Triggered when the session starts. Sets some event handlers
        
        """
        JabberClient.session_started(self)
        self.stream.set_message_handler("normal", self.received)
        self.stream.set_message_handler("error", self.error_received)

    def controller(self):
        """Default controller implementation. Should be overriden in
        derived classes.
            It returns a list of the form [(regex, method), ...] 
        received messages will be matched against the regexs and the
        corresponding method will be called in the first one that 
        matches
        
        """
        return [(r".*", self.default)]
    
    def controller_from_bot_methods(self):
        """Takes all methods of the class in the form bot_* and returns
        a controller list in the form [(regex matching the name of the
        method without bot_, method)]

        """
        botregex = re.compile(r"^bot_.+")
        botmethods = [method for method in dir(self) 
                                    if callable(getattr(self,method))
                                       and botregex.match(method)]
        regexes = ["^"+method[4:]+".*" for method in botmethods]
        return zip(regexes, [getattr(self, method) for method in botmethods])

    def received(self, stanza):
        """Handler for normal messages. 

        """
        if not stanza.get_body():
            return
        for pat, fun in self.controller():
            if re.compile(pat).match(stanza.get_body()):
                self.send(self.get_reply_stanza(stanza, fun))
                return

    def error_received(self, stanza):
        """Handler for error messages.
        Should be overriden in derived classes

        """
        print stanza.get_body()

    def default(self, stanza):
        """Sample default response, acts as an echo bot
            Should be overriden in derived classes

        """
        return Message(to_jid=stanza.get_from(), 
                body=stanza.get_body())
    
    def send(self, stanza):
        """Replies to a stanza"""
        self.stream.send(stanza)

    def get_reply_stanza(self, stanza, fun):
        """Gets a reply to a stanza from aplying fun to
        the stanza's body

        """
        return fun(stanza)

    def start(self):
        """Connects to the server and starts waiting for input"""
        self.connect()
        self.loop()

    def loop(self, timeout=1):
        """Loop method, this will be run until client is disconnected
        waits for client input and runs events

        """
        while 1:
            stream=self.get_stream()
            if not stream:
                break
            act=stream.loop_iter(timeout)
            self.__time_elapsed+=timeout
            if not act:
                self.check_events(timeout)
                self.idle()

    def check_events(self, step):
        for event in self.__events:
            event.elapsed+=step
            if event.elapsed >= event.timeout:
                event.elapsed = 0
                event.fun()

    def add_event(self, fun, timeout, elapsed=0):
        self.__events.append(Event(fun, timeout, elapsed))


class Event():
    def __init__(self, fun, timeout, elapsed=0):
        self.fun = fun
        self.timeout = timeout
        self.elapsed = elapsed


if __name__ == "__main__":
    BaseBot("botiboti@127.0.0.1", "b3rb3r3ch0").start()
