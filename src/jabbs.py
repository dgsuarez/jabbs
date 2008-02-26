import re
import threading
import Queue
import logging
import types
import enum

from pyxmpp.all import JID, Iq, Presence, Message, StreamError
from pyxmpp.jabber.muc import MucRoomHandler, MucRoomManager
from pyxmpp.jabber.client import JabberClient


class Core(JabberClient):
    """Core of the framework, handles connections and dispatches messages 
    to the corresponding Conversation"""
    def __init__(self, jid, passwd, starter=None, starter_params={}, user_control=(lambda x:True), default_nick="botiboti", rooms_to_join=[]):
        """Initializes the bot with jid (node@domain) and it's
        password.

        starter and starter_params are the class of the first controller to be used and
        it's params. If none is provided a default controller will be used.
        
        user_control is a function to determine if a user should be accepted if he requests
        so with a suscribe presence stanza. Must return True/False

        """
        self.__time_elapsed = 0
        self.__events = []
        self.conversations = {}
        self.user_control = user_control
        self.jid = self.create_jid(jid)
        self.default_nick = default_nick
        if not starter:
            starter = Controller
        self.__starter = starter
        self.__starter_params = starter_params
        self.initialize_logger()
        self.rooms_to_join = rooms_to_join
        JabberClient.__init__(self, self.jid, passwd)

    def initialize_logger(self):
        """Initializes logger"""
        self.logger = logging.getLogger("logger")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)
    
    def create_jid(self, jid):
        """Creates an apropiate jid"""
        jid_ = JID(jid)
        if not jid_.resource:
            return JID(jid_.node, jid_.domain, self.__class__.__name__)
        return jid_
        
    def session_started(self):
        """Triggered when the session starts. Sets some event handlers and
        connects to indicated rooms
        
        """
        JabberClient.session_started(self)
        self.stream.set_message_handler("chat", self.received_chat)
        self.stream.set_message_handler("error", self.error_received)
        self.stream.set_presence_handler("subscribe",self.received_presence)
        self.stream.set_presence_handler("unsubscribe",self.received_presence)
        self.stream.set_presence_handler("subscribed",self.received_presence)
        self.stream.set_presence_handler("unsubscribed",self.received_presence)
        self.logger.info("Session started")
        self.mucman = MucRoomManager(self.stream)
        self.mucman.set_handlers()
        for room in self.rooms_to_join:
            self.join_room(JID(room))
        
        
    def join_room(self, jid):
        room_jid=JID(jid)
        self.mucman.join(room_jid, self.default_nick, RoomHandler(self))
        queue_out = Queue.Queue(5)
        queue_in = Queue.Queue(5)
        self.conversations[room_jid] = ConversationQueues(queue_in, queue_out)
        Conversation(room_jid, 
                     self.__starter, 
                     self.__starter_params, 
                     ConversationQueues(queue_out, queue_in),
                     "groupchat"
                     ).start()
        self.logger.info("Started new conversation in %s", room_jid.as_string())
        self.logger.debug("Thread list: %s", threading.enumerate())
        
    def start_conversation(self, jid):
        """Spans a new thread for a new conversation, which is associated to jid"""
        queue_out = Queue.Queue(5)
        queue_in = Queue.Queue(5)
        self.conversations[jid] = ConversationQueues(queue_in, queue_out)
        Conversation(jid, 
                     self.__starter, 
                     self.__starter_params, 
                     ConversationQueues(queue_out, queue_in),
                     "chat"
                     ).start()
        self.logger.info("Started new conversation with %s@%s", jid.node, jid.domain)
        self.logger.debug("Thread list: %s", threading.enumerate())
        
        
    def received_chat(self, stanza):
        """Handler for chat messages"""
        self.logger.info("Received %s message from %s@%s",stanza.get_type(), stanza.get_from().node, stanza.get_from().domain)
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        if stanza.get_from() not in self.conversations.keys():
            self.start_conversation(stanza.get_from())
        self.conversations[stanza.get_from()].queue_out.put(stanza)
        ans=self.conversations[stanza.get_from()].queue_in.get()
        if ans.type == MessageWrapper.message_types.end:
            self.send(ans.stanza)
            del self.conversations[stanza.get_from()]
            self.logger.info("Conversation with %s@%s ended", stanza.get_from().node, stanza.get_from().domain)
        else:
            self.send(ans.stanza)
            
    def received_groupchat(self, user, stanza):
        """Handler for groupchat messages"""
        self.logger.info("Received %s message from %s", stanza.get_from().as_string())
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        self.conversations[stanza.get_from().bare()].queue_out.put(stanza)
        ans=self.conversations[stanza.get_from().bare()].queue_in.get()
        if ans.type == MessageWrapper.message_types.end:
            self.send(ans.stanza)
            del self.conversations[stanza.get_from().bare()]
            self.logger.info("Groupchat in %s ended", stanza.get_from().as_string())
        else:
            self.send(ans.stanza)
            
    def received_presence(self, stanza):
        """Handler for subscription stanzas"""
        self.logger.info("Received %s request from %s", stanza.get_type(), stanza.get_from())
        if self.user_control(stanza.get_from()):
            self.send(stanza.make_accept_response())
        else:
            self.send(stanza.make_deny_response())
        
    def error_received(self, stanza):
        """Handler for error messages"""
        print stanza.get_body()

    def send(self, stanza):
        """Replies to a stanza"""
        self.logger.debug("stanza to send: %s", stanza.serialize())
        self.stream.send(stanza)

    def start(self):
        """Connects to the server and starts waiting for input"""
        self.connect()
        self.loop()

    def loop(self, timeout=1):
        """Loop method, waits for client input and runs events"""
        while 1:
            stream = self.get_stream()
            if not stream:
                break
            act = stream.loop_iter(timeout)
            self.__time_elapsed += timeout
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


class Conversation (threading.Thread):
    """Conversation thread. Takes care of a single conversation.
    Multiple conversations can be run in parallel, one for each jid"""
    def __init__(self, jid, controller, controller_params, queues, type): 
        self.jid = jid
        self.controller = controller(conversation=self, type=type, **controller_params)
        self.queues = queues
        self.__next_stanza_id = 0
        threading.Thread.__init__(self)
        self.__stop = False
    
    def run(self):
        """Waits for input from the core and answers back"""
        while not self.__stop:
            stanza = self.queues.queue_in.get()
            self.queues.queue_out.put(self.get_reply(stanza))
    
    def end(self):
        """Ends the session with the user"""
        self.__stop = True
        
    def get_reply(self, stanza):
        """Replies to stanza according to the controller"""
        for pat, fun in self.controller.controller():
            if re.compile(pat).match(stanza.get_body()):
                ans=fun(stanza)
                if ans.type == MessageWrapper.message_types.end:
                    self.end()
                return ans
    
    def get_next_stanza_id(self):
        """Returns next stanza id for the session"""
        self.__next_stanza_id += 1
        return "jabbsconv%d" % self.__next_stanza_id
    
    next_stanza_id=property(get_next_stanza_id)
    
    def transfer(self, controller):
        """Transfers control to a new controller"""
        self.controller = controller
        self.controller.conversation = self


class MessageWrapper:
    """Wrapper for stanzas between the core and the conversations,
    so additional information can be added"""
    message_types = enum.Enum("stanza", "end")
    
    def __init__(self, type=message_types.stanza, stanza=None):
        self.stanza = stanza
        self.type = type

class ConversationQueues:
    """Queues needed for communicating the core and a conversation"""
    def __init__(self, queue_in, queue_out):
        self.queue_in = queue_in
        self.queue_out = queue_out

class RoomHandler(MucRoomHandler):
    
    def __init__(self, core):
        self.core = core
        self.logger = logging.getLogger("logger")
        
    def message_received(self, user, stanza):
        if self.room_state.get_nick() == stanza.get_from().resource:
            return
        self.logger.info("received stanza: "+ stanza.serialize())
        self.core.received_groupchat(user, stanza)
        
    def error(self, stanza):
        self.logger.info("received error stanza: "+ stanza.serialize())
            
class Controller:
    """Controller base class. Controllers must inherit from this one"""
    def __init__(self, conversation=None, type="chat"):
        self.conversation = conversation
        self.type = type
        
    def controller(self):
        """Sample default controller implementation. 
            It returns a list of the form [(regex, method), ...] 
        received messages will be matched against the regexs and the
        corresponding method will be called in the first one that 
        matches
        
        """
        return [(r".*", self.default)]
    
    def default(self, stanza):
        """Sample default response, acts as an echo bot"""
        return self.message(stanza.get_body())

    def error_handler(self, stanza):
        """Sample error handler"""
        print stanza


    def message(self, body):
        """Creates a message to the jids associated with the controller"""
        return MessageWrapper(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type=self.type,
                                             stanza_id=self.conversation.next_stanza_id),
                              type=MessageWrapper.message_types.stanza)
        
    def end(self, body):
        """Returns an end message"""
        return MessageWrapper(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type="chat",
                                             stanza_id=self.conversation.next_stanza_id),
                              type=MessageWrapper.message_types.end)
        

class Event:
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


def controller_from_bot_methods(controller):
        """Takes all methods of the instance in the form bot_* and returns
        a controller list in the form [(regex matching the name of the
        method without bot_, method)]

        """
        botregex = re.compile(r"^bot_.+")
        botmethods = [method for method in dir(controller) 
                                    if callable(getattr(controller,method))
                                       and botregex.match(method)]
        regexes = ["^"+method[4:]+".*" for method in botmethods]
        return zip(regexes, [getattr(controller, method) for method in botmethods])


if __name__ == "__main__":
    Core("botiboti@127.0.0.1", "b3rb3r3ch0", rooms_to_join=["chats@conference.127.0.0.1"]).start()
