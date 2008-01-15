import re

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient


class Core(JabberClient):

    def __init__(self, jid, passwd, starter=None, starter_params={}):
        """Initializes the bot with jid (username@jabberserver) and it's
        password.

        starter is the class of the first controller to be used. If none 
        is provided a default controller will be used.

        """
        self.__time_elapsed=0
        self.__events=[]
        jid_ = JID(jid)
        self.users = {}
        if not jid_.resource:
            jid_=JID(jid_.node, jid_.domain, self.__class__.__name__)
        JabberClient.__init__(self, jid_, passwd)
        if not starter:
            starter=Controller
        self.__starter=starter
        self.__starter_params=starter_params

    def session_started(self):
        """Triggered when the session starts. Sets some event handlers
        
        """
        JabberClient.session_started(self)
        self.stream.set_message_handler("normal", self.received)
        self.stream.set_message_handler("error", self.error_received)
   
    def transfer(self, controller, jid):
        """Transfers control to another bot, and if possible,
        notifies the bot about this instance so control can come
        back
        
        """
        self.users[str(jid)]=controller
        if "set_info" in dir(controller):
            controller.set_info(self, jid)

    def received(self, stanza):
        """Handler for normal messages"""
        if not stanza.get_body():
            return
        if str(stanza.get_from()) not in self.users.keys():
            self.transfer(self.__starter(**self.__starter_params), stanza.get_from())
            #self.users.keys[str(stanza.get_from())]=self.__starter(**self.__starter_params)
        for pat, fun in self.users[str(stanza.get_from())].controller():
            if re.compile(pat).match(stanza.get_body()):
                self.send(self.get_reply_stanza(stanza, fun))
                return

    def error_received(self, stanza):
        """Handler for error messages."""
        print stanza.get_body()

       
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
        """Checks all events"""
        for event in self.__events:
            event.check(step)

    def add_event(self, event):
        """Adds a new event to the list of events"""
        self.__events.append(event)


class Controller():

    def controller(self):
        """Sample default controller implementation. 
            It returns a list of the form [(regex, method), ...] 
        received messages will be matched against the regexs and the
        corresponding method will be called in the first one that 
        matches
        
        """
        return [(r".*", self.default)]
    
    def default(self, stanza):
        """Sample default response, acts as an echo bot

        """
        return Message(to_jid=stanza.get_from(), 
                body=stanza.get_body())

    def error_handler(self, stanza):
        """Sample error handler"""
        print stanza
 
    def set_info(self, caller, jid):
        """Is called by the core to notify about itself"""
        self.jid = jid
        self.core = caller

    def message(self, body):
        """Creates a message to the jid associated with the controller"""
        return Message(to_jid=self.jid, body=body)


class Event():
    """Encapsulates an event: the function that should be called and the time
    that needs to be elapsed between calls
    
    """
    def __init__(self, fun, timeout, elapsed=0, args={}):
        """Initializes an event with the callback function, the timeout of the call
        and optionally elapsed time for the first call

        """
        self.fun = fun
        self.timeout = timeout
        self.elapsed = elapsed
        self.args = args

    def check(self, step):
        """Checks if the callback should be made, and if it should it makes it"""
        self.elapsed+=step
        if self.elapsed >= self.timeout:
            self.elapsed = 0
            self.fun(**self.args)



def controller_from_bot_methods(instance):
        """Takes all methods of the instance in the form bot_* and returns
        a controller list in the form [(regex matching the name of the
        method without bot_, method)]

        """
        botregex = re.compile(r"^bot_.+")
        botmethods = [method for method in dir(instance) 
                                    if callable(getattr(instance,method))
                                       and botregex.match(method)]
        regexes = ["^"+method[4:]+".*" for method in botmethods]
        return zip(regexes, [getattr(instance, method) for method in botmethods])


if __name__ == "__main__":
    Core("botiboti@127.0.0.1", "b3rb3r3ch0").start()
