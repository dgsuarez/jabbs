import re

from jabbs import controller, core

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class Minuteman (controller.Controller):
    
    def __init__(self, conversation, type):
        self.minutes = open("minutes.txt", 'w')
        self.scribe = None
        self.title = None
        self.chair = None
        self.topics = []
        self.current_minute = None
        controller.Controller.__init__(self, conversation, type)
        
    def controller(self):
        return [("I'm the scribe", self.set_scribe),
                ("I am the scribe", self.set_scribe),
                ("^Topic:.*", self.add_topic),
                ("^Chair:.*", self.set_chair),
                ("^Title:.*", self.set_title),
                ("^Minutes info", self.show_info),
                ("^To be minuted: .*",self.minute),
                ("\.\.\..*", self.continue_minute),
                ("End minutes", self.end_minutes)
                ]
        
    def set_scribe(self, stanza):
        if self.scribe:
            return self.message("Scribe is already set")
        self.scribe = stanza.get_from().resource
        self.minutes.write("Scribe: "+self.scribe+"\n")
        return self.message("Scribe set to: "+self.scribe, self.type)
    
    def set_chair(self, stanza):
        if stanza.get_from().resource != self.scribe:
            return self.message("Only the scribe can set the chair. If you havent, set a scribe")    
        self.chair = re.sub("^Chair: ","",stanza.get_body())
        self.minutes.write("Chair: "+self.chair+"\n")
        return self.message("Chair is: "+self.chair)
    
    def set_title(self, stanza):
        if stanza.get_from().resource != self.scribe:
            return self.message("Only the scribe can set the title. If you havent, set a scribe")    
        self.title = re.sub("^Title: ", "", stanza.get_body())
        self.minutes.write("Title: "+self.title+"\n")
        return self.message("Title is: "+self.title)   
        
    def add_topic(self, stanza):
        if stanza.get_from().resource != self.scribe:
            return self.message("Only the scribe can set the topic. If you havent, set a scribe")    
        if self.current_minute:
            self.minutes.write(self.current_minute)
        self.topics.append(re.sub("^Topic: ","",stanza.get_body()))
        self.minutes.write("Topic: "+self.topics[-1]+"\n")
        return self.message("Topic is: "+self.topics[-1])
    
    def show_info(self, stanza):
        ret = "Title: %s\n Chair: %s\n Scribe: %s\n Topics: %s" % (self.title, 
                                                                   self.chair, 
                                                                   self.scribe, 
                                                                   ",".join(self.topics))
        return self.message(ret)

    def minute(self,stanza):
        if stanza.get_from().resource != self.scribe:
            return self.message("Only the scribe can add minutes. If you havent, set a scribe")
        if self.current_minute:
            self.minutes.write(str(self.current_minute))
            self.minutes.flush()
        parts = stanza.get_body().split(":",2)
        self.current_minute=Minute(parts[1])
        self.current_minute.text.append(parts[2])
        return self.no_message()
    
    def continue_minute(self, stanza):
        if stanza.get_from().resource != self.scribe:
            return self.no_message()
        self.current_minute.text.append(re.sub("^\.\.\.","",stanza.get_body()))
        return self.no_message()

    def end_minutes(self, stanza):
        if self.current_minute:
            self.minutes.write(str(self.current_minute))
        if self.conversation.room_state:
            attendees = self.conversation.room_state.users.keys()
            self.minutes.write("Attendees: "+",".join(attendees))
        self.minutes.close()
        return self.end("Minutes ended")

class Minute:
    
    def __init__(self, author):
        self.author = author
        self.text = []
        
    def __str__(self):
        return self.author+" says: "+"\n\t".join(self.text)+"\n"
        
if __name__=="__main__":
    core.Core("botiboti@127.0.0.1", "b3rb3r3ch0", Minuteman, rooms_to_join=["chats@conference.127.0.0.1"]).start()