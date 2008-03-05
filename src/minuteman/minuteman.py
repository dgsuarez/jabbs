import re

from jabbs import controller, core

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

from models import Minutes, Topic, Statement, Participant
import models

class Minuteman (controller.Controller):
    
    def __init__(self, conversation):
        self.db_session = models.get_session()
        self.minutes = Minutes()
        controller.Controller.__init__(self, conversation)
        
    def controller(self):
        return [("I'm the scribe", self.set_scribe),
                ("I am the scribe", self.set_scribe),
                ("^Topic:.*", self.add_topic),
                ("^Chair:.*", self.set_chair),
                ("^Title:.*", self.set_title),
                ("^Minutes info", self.show_info),
                ("^To be minuted: .*",self.add_statement),
                ("\.\.\..*", self.continue_statement),
                ("Show minutes", self.show_info),
                ("End minutes", self.end_minutes)
                ]
        
    def set_scribe(self, stanza):
        if self.minutes.scribe:
            return self.message("Scribe is already set")
        self.minutes.scribe = stanza.get_from().resource
        self.db_session.save(self.minutes)
        return self.message("Scribe set to: "+self.minutes.scribe)
    
    def set_chair(self, stanza):
        if not self.is_sent_by_scribe(stanza):
            return self.message("Only the scribe can set the chair. If you havent, set a scribe")    
        self.minutes.chair = re.sub("^Chair: ","",stanza.get_body())
        return self.message("Chair is: "+self.minutes.chair)
    
    def set_title(self, stanza):
        if not self.is_sent_by_scribe(stanza):
            return self.message("Only the scribe can set the title. If you havent, set a scribe")    
        self.minutes.title = re.sub("^Title: ", "", stanza.get_body())
        return self.message("Title is: "+self.minutes.title)   
        
    def add_topic(self, stanza):
        if not self.is_sent_by_scribe(stanza):
            return self.message("Only the scribe can set a topic. If you havent, set a scribe")    
        self.minutes.topics.append(Topic(re.sub("^Topic: ","",stanza.get_body())))
        return self.message("Topic is: "+self.minutes.topics[-1].title)
    
    def is_sent_by_scribe(self, stanza):
        if stanza.get_from().resource == self.minutes.scribe:
            return True
        return False

    def show_info(self, stanza):
        ret = str(self.minutes)
        return self.message(ret)

    def add_statement(self,stanza):
        if not self.is_sent_by_scribe(stanza):
            return self.message("Only the scribe can add minutes. If you havent, set a scribe")
        if len(self.minutes.topics) == 0:
            return self.message("Before submiting a minute you must submit a topic")
        parts = stanza.get_body().split(":",2)
        self.minutes.topics[-1].statements.append(Statement(parts[1],parts[2]))
        return self.no_message()
    
    def continue_statement(self, stanza):
        if not self.is_sent_by_scribe(stanza):
            return self.no_message()
        if len(self.minutes.topics) == 0:
            return self.message("Before submiting a minute you must submit a topic")
        if len(self.minutes.topics[-1].statements) == 0:
            return self.message("Before continuing a minute you must submit one")
        self.minutes.topics[-1].statements[-1].text += ("\n%s" %(re.sub("^\.\.\.","",stanza.get_body())))
        return self.no_message()

    def end_minutes(self, stanza):
        if self.conversation.room_state:
            attendees = self.conversation.room_state.users.keys()
            for i in attendees:
                self.minutes.participants.append(Participant(i))
        self.db_session.commit()
        return self.end("Minutes ended")


class MinutesManager(controller.Controller):
    
    def __init__(self, conversation):
        self.db_session = models.get_session()
        controller.Controller.__init__(self, conversation)
    
    def controller(self):
        return [("Show minutes", self.show_available_minutes),
                ("Select minutes", self.select_minute_to_show)
                ]
        
    def show_available_minutes(self, stanza):
        return self.message("\n".join("%s: %s" % (str(i.date), i.title) for i in self.db_session.query(Minutes)))
    
    def select_minute_to_show(self, stanza):
        options = [(i.id, i.title) for i in self.db_session.query(Minutes)]
        id, title = self.conversation.get_selection_from_options(options, "Available minutes are:")
        return self.message(
                            str(self.db_session.query(Minutes).filter_by(id=id)[0])
                            )
    

if __name__=="__main__":
    core.Core("botiboti@127.0.0.1", "b3rb3r3ch0", MinutesManager, rooms_to_join=["chats@conference.127.0.0.1"]).start()
    