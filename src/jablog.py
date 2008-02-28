import jabbs

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class Jablog(jabbs.Controller):
    
    def __init__(self, conversation, type):
        self.file = open("log.txt", 'w')
        jabbs.Controller.__init__(self, conversation, type)
        
    def controller(self):
        return [("^end_logging", self.bye),
                (".*", self.log)]
    
    def log(self, stanza):
        self.file.write( stanza.get_from().as_string() + "> " + stanza.get_body() +"\n")
        return self.no_message()
    
    def bye(self, stanza):
        self.file.close()
        return self.end("ended logging")
        
if __name__=="__main__":
    jabbs.Core("botiboti@127.0.0.1", "b3rb3r3ch0", Jablog, rooms_to_join=["chats@conference.127.0.0.1"]).start()