from jabbs import core, basic

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class JablogDispatcher(basic.Dispatcher):
    
    def __init__(self, conversation):
        self.jablog = Jablog(conversation.info)
        basic.Dispatcher.__init__(self, conversation)
        
    def dispatcher(self):
        return [("^end_logging", self.jablog.bye),
                (".*", self.jablog.log)]


class Jablog(basic.Messenger):
    def __init__(self, conversation_info):
        self.file = open("%s@%s_log.txt" % (conversation_info.jid.node, conversation_info.jid.domain), 'a')
        basic.Messenger.__init__(self, conversation_info)
        
    def log(self, stanza):
        self.file.write( "<"+stanza.get_from().as_string()+"> "+stanza.get_body()+"\n")
        return self.no_message()
    
    def bye(self, stanza):
        self.file.write("---------------------------------\n\n")
        self.file.close()
        return self.end("ended logging")
if __name__=="__main__":
    core.Core("config.cfg").start()