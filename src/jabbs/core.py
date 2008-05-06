import re
import threading
import Queue
import logging

import messagetypes

from pyxmpp.all import JID, Iq, Presence, Message, StreamError
from pyxmpp.jabber.muc import MucRoomHandler, MucRoomManager
from pyxmpp.jabber.client import JabberClient

import configparser

class Core(JabberClient):
    """Core of the framework, handles connections and dispatches messages 
    to the corresponding Conversation"""
    def __init__(self, config_path):
        """Initializes the bot with data from a configuration file 
        
        jid (node@domain) and it's password.

        starter and starter_params are the class of the first controller to be used and
        it's params. If none is provided a default controller will be used.
        
        user_control is a function to determine if a user should be accepted if he requests
        so with a suscribe presence stanza. Must return True/False

        """
        self.initialize_logger()
        self.config = configparser.Config(config_path)
        self.conversations = {}
        self.user_control = self.config.user_control
        self.jid = self.create_jid(self.config.jid)
        self.nick = self.config.nick
        self.__starter = self.config.starter
        self.__starter_params = self.config.starter_params
        self.rooms_to_join = self.config.rooms_to_join
        self.start_on_user_connect = self.config.start_on_user_connect
        JabberClient.__init__(self, self.jid, self.config.password)

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
        self.stream.set_message_handler("chat", self.chat_received)
        self.stream.set_message_handler("error", self.error_received)
        self.stream.set_presence_handler(None,self.presence_received)
        self.stream.set_presence_handler("unavailable",self.unavailable_received)
        self.stream.set_presence_handler("subscribe",self.subscription_received)
        self.stream.set_presence_handler("unsubscribe",self.subscription_received)
        self.stream.set_presence_handler("subscribed",self.subscription_received)
        self.stream.set_presence_handler("unsubscribed",self.subscription_received)
        self.logger.info("Session started")
        self.mucman = MucRoomManager(self.stream)
        self.mucman.set_handlers()
        for room in self.rooms_to_join:
            self.join_room(JID(room))
        
    def join_room(self, jid):
        """Joins the room jid, starting a new thread for its messages"""
        room_jid=JID(jid)
        handler = RoomHandler(self)
        self.mucman.join(room_jid, self.nick, handler)
        room_state = handler.room_state
        self.start_conversation(room_jid, "groupchat", room_state)
        
    def start_conversation(self, jid, type="chat", room_state = None):
        """Spans a new thread for a new conversation, which is associated to jid
        Checks if the jid is allowed to use the application using user_control
        """
        if not self.user_control(jid):
            self.send(Message(to_jid=jid,
                              stanza_type=type,
                              from_jid=self.jid,
                              body="You are not allowed to talk with me"))
            return False
        queue_out = Queue.Queue(5)
        queue_in = Queue.Queue(5)
        self.conversations[jid] = ConversationQueues(queue_in, queue_out)
        Conversation(jid, 
                     self.__starter, 
                     self.__starter_params, 
                     ConversationQueues(queue_out, queue_in),
                     type,
                     room_state
                     ).start()
        self.logger.info("Started new conversation with %s@%s", jid.node, jid.domain)
        self.logger.debug("Thread list: %s", threading.enumerate())
        return True
        
    def chat_received(self, stanza):
        """Handler for chat messages"""
        self.logger.info("Received %s ",stanza.serialize())
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        if stanza.get_from() not in self.conversations.keys():
            if not self.start_conversation(stanza.get_from()):
                return
        self.conversations[stanza.get_from()].queue_out.put(messagetypes.StanzaMessage(stanza.copy()))
            
    def groupchat_received(self, user, stanza):
        """Handler for groupchat messages"""
        self.logger.info("Received %s message from %s", stanza.get_type(), stanza.get_from().as_string())
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        self.conversations[stanza.get_from().bare()].queue_out.put(messagetypes.StanzaMessage(stanza.copy()))
    
    def process_conversation_message(self, ans):
        """Process any kind of message stanza coming from a conversation"""
        if ans.__class__ == messagetypes.EndMessage:
            self.send(ans.stanza)
            del self.conversations[ans.stanza.get_to()]
            self.logger.info("Conversation with %s@%s/%s ended", 
                             ans.stanza.get_to().node, 
                             ans.stanza.get_to().domain, 
                             ans.stanza.get_to().resource)
        elif ans.__class__ == messagetypes.NoMessage:
            return
        else:
            self.send(ans.stanza)
    
    def check_for_messages(self):
        """Checks if messages from conversations are available. If so 
        calls process_received to process them
        
        """
        for jid, queues in self.conversations.items():
            try:
                ans = queues.queue_in.get(False)
                if ans:
                    self.process_conversation_message(ans)
            except Queue.Empty:
                pass
        
    def subscription_received(self, stanza):
        """Handler for subscription stanzas"""
        self.logger.info("Received %s request from %s", stanza.get_type(), stanza.get_from())
        if self.user_control(stanza.get_from()):
            self.send(stanza.make_accept_response())
        else:
            self.send(stanza.make_deny_response())
            
    def presence_received(self, stanza):
        """Handler for initial presence received from users"""
        if stanza.get_from() in self.conversations:
            return
        if not self.start_on_user_connect:
            return
        if not self.start_conversation(stanza.get_from()):
            return
        self.conversations[stanza.get_from()].queue_out.put(messagetypes.UserConnected())
            
    def unavailable_received(self, stanza):
        """Handler for unavailable presence received from users"""
        if not stanza.get_from() in self.conversations:
            return
        self.conversations[stanza.get_from()].queue_out.put(messagetypes.UserDisconnected())
        
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
        """Loop method, waits for client input and reacts to it"""
        while 1:
            stream = self.get_stream()
            if not stream:
                break
            act = stream.loop_iter(timeout)
            self.check_for_messages()
            if not act:
                self.idle()


class ConversationInfo:
    """Information about a conversation"""
    def __init__(self, jid, type, room_state):
        self.jid = jid
        self.type = type
        self.room_state = room_state
        self.__next_stanza_id = 0
        
    def get_next_stanza_id(self):
        """Returns next stanza id for the session"""
        self.__next_stanza_id += 1
        return "jabbsconv%d" % self.__next_stanza_id
    next_stanza_id=property(get_next_stanza_id)
    
    
class Conversation(threading.Thread):
    """Conversation thread. Takes care of a single conversation.
    Multiple conversations can be run in parallel, one for each jid"""
    def __init__(self, jid, dispatcher, dispatcher_params, queues, type, room_state): 
        self.info = ConversationInfo(jid, type, room_state)
        self.queues = queues
        self.__stop = False
        self.transfer(dispatcher(self, **dispatcher_params))
        threading.Thread.__init__(self)
    
    def run(self):
        """Waits for input from the core and answers back"""
        while not self.__stop:
            stanza = self.queues.queue_in.get()
            ans = self.get_reply(stanza)
            self.queues.queue_out.put(ans)
        
    def get_reply(self, message):
        """Processes received messages from the core"""
        if isinstance(message, messagetypes.StanzaMessage):
            return self.get_reply_to_stanza(message)
        else:
            return self.get_reply_to_status_change(message)
    
    def get_reply_to_status_change(self, message):
        """Calls connection methods on the dispatcher"""
        if isinstance(message, messagetypes.UserConnected):
            return self.dispatcher.on_user_connect()
        elif isinstance(message, messagetypes.UserDisconnected):
            return self.dispatcher.on_user_disconnect()
        
    def get_reply_to_stanza(self, message):
        """Replies to stanza according to the dispatcher"""
        for pat, fun in self.dispatcher.dispatcher():
            match = re.compile(pat).search(message.stanza.get_body())
            if match:
                ans = fun(message.stanza, *match.groups())
                return self.process_message_to_send(ans)
        return messagetypes.NoMessage()
    
    def process_message_to_send(self, to_send):
        """Processes a message from the user"""
        if isinstance(to_send, messagetypes.Question):
            return self.ask_question(to_send)
        elif isinstance(to_send, messagetypes.EndMessage):
            self.end()
        return to_send

    def ask_question(self, to_send):
        """Asks questions to the user"""
        if isinstance(to_send, messagetypes.MultipleChoiceQuestion):
            ans = self.ask_multiple_choice_question(to_send.question, to_send.options)
            return to_send.callback(*ans)
        elif isinstance(to_send, messagetypes.YesNoQuestion):
            ans = self.ask_yes_no_question(to_send.question)
            return to_send.callback(ans)
        elif isinstance(to_send, messagetypes.Question):
            ans = self.ask_regular_question(to_send.question)
            return to_send.callback(ans)
    
    def end(self):
        """Ends the session with the user"""
        self.__stop = True

    def transfer(self, dispatcher):
        """Transfers control to a new dispatcher"""
        self.dispatcher = dispatcher
        self.dispatcher.conversation = self
        
    def ask_multiple_choice_question(self, text, options):
        """Sends a list of posible options and returns the user's choice 
        to the caller
        
        """
        m = "\n".join("%s) %s" % (str(i), text) for i, text in options)
        s = messagetypes.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=text+"\n"+m,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        stanza = self.queues.queue_in.get().stanza
        try:
            option = stanza.get_body().strip()
            for o, t in options:
                if str(o).strip() == option:
                    return (o, t)
            raise Exception, "Options not well formed"
            
        except:
            return self.ask_multiple_choice_question("You must input a valid option\n"+text, options)
    
    def ask_regular_question(self, text):
        """Sends a question and returns the answer of the user"""
        s = messagetypes.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=text,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        return self.queues.queue_in.get().stanza.get_body()
    
    def ask_yes_no_question(self, text):
        """Sends a yes/no question and returns the stanza answer of the user"""
        s = messagetypes.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=text,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        ans = self.queues.queue_in.get().stanza.get_body().strip()
        if ans == "yes":
            return True
        if ans == "no":
            return False
        return self.ask_yes_no_question("Please answer yes or no\n"+text)
    
class ConversationQueues:
    """Queues needed for communicating the core and a conversation"""
    def __init__(self, queue_in, queue_out):
        self.queue_in = queue_in
        self.queue_out = queue_out


class RoomHandler(MucRoomHandler):
    """Needed for MUC conversations"""
    def __init__(self, core):
        self.core = core
        self.logger = logging.getLogger("logger")
        
    def message_received(self, user, stanza):
        """Receives a message from a groupchat and returns control back to core"""
        if self.room_state.get_nick() == stanza.get_from().resource:
            return
        self.logger.info("received stanza: "+ stanza.serialize())
        self.core.groupchat_received(user, stanza)
        
    def error(self, stanza):
        self.logger.info("received error stanza: "+ stanza.serialize())

