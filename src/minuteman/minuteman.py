from jabbs import util, controller, core

from models import Minutes, Topic, Statement, Participant
import models
import messages

util.jinja_messages_from_strings(messages)

class Minuteman(controller.Controller):
    
    def __init__(self, conversation=None):
        self.db_session = models.get_session()
        self.minutes = Minutes()
        controller.Controller.__init__(self, conversation)
        
    def controller(self):
        return [("I'm the scribe", self.set_scribe),
                ("I am the scribe", self.set_scribe),
                ("^Topic: (.*)", self.add_topic),
                ("^Chair: (.*)", self.set_chair),
                ("^Title: (.*)", self.set_title),
                ("^Minutes info", self.show_info),
                ("^To be minuted: (.+?): (.+)",self.add_statement),
                ("\.\.\.(.*)", self.continue_statement),
                ("Show minutes", self.show_info),
                ("End minutes", self.end_minutes),
                ("Manage minutes", self.manage_minutes)
                ]
        
    def set_scribe(self, stanza):
        if self.minutes.scribe:
            return self.message(messages.scribe_already_set.render())
        self.minutes.scribe = stanza.get_from().resource
        self.db_session.save(self.minutes)
        return self.message(messages.field_set_to.render(field="Scribe", 
                                                         value=self.minutes.scribe))
    
    def set_chair(self, stanza, chair):
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set the chair"))    
        self.minutes.chair = chair
        return self.message(messages.position_set_to.render(position="Chair",
                                                     name=self.minutes.chair))
    
    def set_title(self, stanza, title):
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set the title"))    
        self.minutes.title = title
        return self.message(messages.field_set_to.render(field="Title", 
                                                         value=self.minutes.title))  
        
    def add_topic(self, stanza, topic):
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set a topic"))    
        self.minutes.topics.append(Topic(topic))
        return self.message(messages.field_set_to.render(field="Topic", 
                                                         value=self.minutes.topics[-1].title))
    
    def is_sent_by_scribe(self, stanza):
        if stanza.get_from().resource == self.minutes.scribe:
            return True
        return False

    def show_info(self, stanza):
        return self.message(messages.show_minutes.render(minutes=self.minutes))

    def add_statement(self, stanza, author, statement):
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="add minutes"))
        if len(self.minutes.topics) == 0:
            return self.message(messages.no_topic_for_minute.render())
        self.minutes.topics[-1].statements.append(Statement(author, statement))
        return self.no_message()
    
    def continue_statement(self, stanza, statement):
        if not self.is_sent_by_scribe(stanza):
            return self.no_message()
        if len(self.minutes.topics) == 0:
            return self.message(messages.no_topic_for_minute.render())
        if len(self.minutes.topics[-1].statements) == 0:
            return self.message(messages.no_minute_to_continue.render())
        self.minutes.topics[-1].statements[-1].text += ("\n%s" %(statement))
        return self.no_message()

    def end_minutes(self, stanza):
        if self.conversation.room_state:
            attendees = self.conversation.room_state.users.keys()
            for i in attendees:
                self.minutes.participants.append(Participant(i))
        self.db_session.commit()
        return self.end(messages.minutes_ended.render())
    
    def manage_minutes(self, stanza):
        self.conversation.transfer(MinutesManager())

class MinutesManager(controller.Controller):
    
    def __init__(self, conversation=None):
        self.db_session = models.get_session()
        controller.Controller.__init__(self, conversation)
    
    def controller(self):
        return [("Show minutes", self.show_available_minutes),
                ("Select minutes", self.select_minutes_to_show),
                ("Remove minutes", self.remove_minutes),
                ("Start minutes", self.start_minutes)
                ]
        
    def show_available_minutes(self, stanza):
        return self.message(messages.show_available_minutes.render(minutes_list=self.db_session.query(Minutes)))
    
    def select_minutes_to_show(self, stanza):
        options = [(i.id, i.title) for i in self.db_session.query(Minutes)]
        id, title = self.conversation.get_selection_from_options(options, messages.available_minutes_are.render())
        return self.message(messages.show_minutes.render(minutes=self.db_session.query(Minutes).filter_by(id=id)[0]))
                            
        
    def remove_minutes(self, stanza):
        id, title = self.conversation.get_selection_from_options([(i.id, i.title) for i in self.db_session.query(Minutes)],
                                                                 messages.select_minutes_to_remove.render())
        try:
            self.db_session.delete(self.db_session.query(Minutes).filter_by(id=id)[0])
            self.db_session.commit()
        except:
            return self.message(messages.error_deleting.render(id=id))
        return self.message(messages.minutes_deleted.render(id=id))
    
    def start_minutes(self, stanza):
        self.conversation.transfer(Minuteman())
    

if __name__=="__main__":
    core.Core("config.cfg").start()
    