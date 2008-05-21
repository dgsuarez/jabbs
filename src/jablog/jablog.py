from jabbs import core, basic


class JablogDispatcher(basic.Dispatcher):
    """Dispatcher for the logger"""
    def __init__(self, conversation):
        self.jablog = Jablog(conversation.info)
        basic.Dispatcher.__init__(self, conversation)
        
    def dispatcher(self):
        """Everything is logged until end_logging is received"""
        return [("^end_logging", self.jablog.bye),
                (".*", self.jablog.log)]


class Jablog(basic.Messenger):
    """Basic logger"""
    def __init__(self, conversation_info):
        """Creates a new file named node@domain_log.txt to log the conversation"""
        self.file = open("%s@%s_log.txt" % (conversation_info.jid.node, conversation_info.jid.domain), 'a')
        basic.Messenger.__init__(self, conversation_info)
        
    def log(self, stanza):
        """Logs a received message"""
        self.file.write( "<"+stanza.get_from().as_string()+"> "+stanza.get_body()+"\n")
        self.file.flush()
        return self.no_message()
    
    def bye(self, stanza):
        """Ends the logging"""
        self.file.write("---------------------------------\n\n")
        self.file.close()
        return self.end("ended logging")
    

if __name__=="__main__":
    core.Core("config.cfg").start()