import core
from messages import StanzaMessage, EndMessage, NoMessage
from pyxmpp.all import JID, Iq, Presence, Message, StreamError

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
        if self.conversation.room_state:
            print self.conversation.room_state.users
        return self.message(stanza.get_body())

    def error_handler(self, stanza):
        """Sample error handler"""
        print stanza

    def message(self, body):
        """Creates a message to the jids associated with the controller"""
        return StanzaMessage(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type=self.type,
                                             stanza_id=self.conversation.next_stanza_id))
        
    def end(self, body):
        """Returns an end message"""
        return EndMessage(stanza=Message(to_jid=self.conversation.jid, 
                                             body=body,
                                             stanza_type=self.type,
                                             stanza_id=self.conversation.next_stanza_id))
        
    
    def no_message(self):
        """Returns a no message"""
        return NoMessage()
    
if __name__ == "__main__":
    core.Core("botiboti@127.0.0.1", "b3rb3r3ch0", starter=Controller,rooms_to_join=["chats@conference.127.0.0.1"]).start()
