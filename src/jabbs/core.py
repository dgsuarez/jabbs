import re
import threading
import Queue
import logging

import messages

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
        """Joins the room jid, starting a new thread for its messages"""
        room_jid=JID(jid)
        handler = RoomHandler(self)
        self.mucman.join(room_jid, self.nick, handler)
        room_state = handler.room_state
        self.start_conversation(room_jid, "groupchat", room_state)
        
    def start_conversation(self, jid, type="chat", room_state = None):
        """Spans a new thread for a new conversation, which is associated to jid"""
        if not self.user_control(jid):
            self.send(Message(to_jid=jid,
                              stanza_type=type,
                              from_jid=self.jid,
                              body="You are not allowed to talk with me"))
            return
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
        
    def received_chat(self, stanza):
        """Handler for chat messages"""
        self.logger.info("Received %s message from %s@%s",stanza.get_type(), stanza.get_from().node, stanza.get_from().domain)
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        if stanza.get_from() not in self.conversations.keys():
            self.start_conversation(stanza.get_from())
        self.conversations[stanza.get_from()].queue_out.put(stanza.copy())
            
    def received_groupchat(self, user, stanza):
        """Handler for groupchat messages"""
        self.logger.info("Received %s message from %s", stanza.get_type(), stanza.get_from().as_string())
        if not stanza.get_body():
            self.logger.info("Message was empty")
            return
        self.conversations[stanza.get_from().bare()].queue_out.put(stanza.copy())
    
    def process_received(self, ans):
        """Process any kind of message stanza"""
        if ans.__class__ == messages.EndMessage:
            self.send(ans.stanza)
            del self.conversations[ans.stanza.get_to()]
            self.logger.info("Conversation with %s@%s/%s ended", 
                             ans.stanza.get_to().node, 
                             ans.stanza.get_to().domain, 
                             ans.stanza.get_to().resource)
        elif ans.__class__ == messages.NoMessage:
            return
        else:
            self.send(ans.stanza)
    
    def check_for_answers(self):
        """Checks if answers from conversations are available. If so 
        calls process_received to process them
        
        """
        for jid, queues in self.conversations.items():
            try:
                ans = queues.queue_in.get(False)
                self.process_received(ans)
            except:
                pass
        
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
        """Loop method, waits for client input and reacts to it"""
        while 1:
            stream = self.get_stream()
            if not stream:
                break
            act = stream.loop_iter(timeout)
            self.check_for_answers()
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
        
    def get_reply(self, stanza):
        """Replies to stanza according to the controller"""
        for pat, fun in self.dispatcher.dispatcher():
            match = re.compile(pat).search(stanza.get_body())
            if match:
                ans = fun(stanza, *match.groups())
                return self.process_answer(ans)
        return messages.NoMessage()

    def process_answer(self, ans):
        """Processes an answer from the user"""
        if ans.__class__ == messages.Question:
            qans = self.ask_question(ans.question)
            return ans.callback(qans)
        elif ans.__class__ == messages.YesNoQuestion:
            ynans = self.ask_yes_no_question(ans.question)
            return ans.callback(ynans)
        elif ans.__class__ == messages.MultipleChoiceQuestion:
            mcqans = self.ask_multiple_choice_question(ans.options, ans.question)
            return ans.callback(*mcqans)
        elif ans.__class__ == messages.EndMessage:
            self.end()
        return ans
    
    def end(self):
        """Ends the session with the user"""
        self.__stop = True
    

    
    def transfer(self, dispatcher):
        """Transfers control to a new controller"""
        self.dispatcher = dispatcher
        self.dispatcher.conversation = self
        
    def ask_multiple_choice_question(self, options, text):
        """Sends a list of posible options and returns the user's choice 
        to the caller
        
        """
        m = "\n".join("%s) %s" % (str(i), text) for i, text in options)
        s = messages.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=text+"\n"+m,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        stanza = self.queues.queue_in.get()
        try:
            option = stanza.get_body().strip()
            for o, t in options:
                if str(o).strip() == option:
                    return (o, t)
            raise Exception()
            
        except:
            return self.ask_multiple_choice_question(options, "You must input a valid option\n"+text)
    
    def ask_question(self, question):
        """Sends a question and returns the answer of the user"""
        s = messages.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=question,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        return self.queues.queue_in.get().get_body()
    
    def ask_yes_no_question(self, question):
        """Sends a yes/no question and returns the stanza answer of the user"""
        s = messages.StanzaMessage(stanza=Message(to_jid=self.info.jid, 
                                             body=question,
                                             stanza_type=self.info.type,
                                             stanza_id=self.info.next_stanza_id))
        self.queues.queue_out.put(s)
        ans = self.queues.queue_in.get().get_body().strip()
        if ans == "yes":
            return True
        if ans == "no":
            return False
        return self.ask_yes_no_question("Please answer yes or no\n"+question)
    
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
        self.core.received_groupchat(user, stanza)
        
    def error(self, stanza):
        self.logger.info("received error stanza: "+ stanza.serialize())

