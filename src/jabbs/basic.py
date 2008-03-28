import core
from messages import *
from pyxmpp.all import JID, Iq, Presence, Message, StreamError

class Dispatcher:
    """Dispatcher base class. Dispatchers must inherit from this one"""
    def __init__(self, conversation):
        self.conversation = conversation
            
    def dispatcher(self):
        """Must be overriden. 
            It returns a list of the form [(regex, method), ...] 
        received messages will be matched against the regexs and the
        corresponding method will be called in the first one that 
        matches
        
        """
        return []

    def error_handler(self, stanza):
        """Sample error handler"""
        print stanza

class Messenger: 
    def __init__(self, conversation_info):
        self.conversation = conversation_info
        
    def message(self, body):
        """Creates a message to the jids associated with the controller"""
        return StanzaMessage(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type=self.conversation.type,
                                             stanza_id=self.conversation.next_stanza_id))
        
    def end(self, body):
        """Returns an end message"""
        return EndMessage(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type=self.conversation.type,
                                             stanza_id=self.conversation.next_stanza_id))
        
    
    def no_message(self):
        """Returns a no message"""
        return NoMessage()
    
    def ask_yes_no_question(self, question, callback):
        return YesNoQuestion(question, callback)
    
    def ask_question(self, question):
        return Question(question, callback)
    
    def ask_multiple_choice_question(self, question, choices, callback):
        return MultipleChoiceQuestion(question, choices, callback)
    
if __name__ == "__main__":
    core.Core("prueba.cfg").start()
