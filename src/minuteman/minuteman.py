from jabbs import util, basic, core

from models import Minutes, Topic, Statement, Participant
import models
import messages

util.jinja_messages_from_strings(messages)

class MainDispatcher(basic.Dispatcher):
    """Default dispatcher"""
    def __init__(self, conversation):
        self.minuteman_dispatcher = MinutemanDispatcher(conversation, self)
        self.minutes_manager_dispatcher = MinutesManagerDispatcher(conversation, self)
        basic.Dispatcher.__init__(self,conversation)
        
    def dispatcher(self):
        """Can start managing minutes or minuting"""
        return [
        ("Manage minutes", self.manage_minutes),
        ("Start minutes", self.start_minutes)
        ]
        
    def manage_minutes(self, stanza):
        """Starts managing minutes"""
        self.conversation.transfer(self.minutes_manager_dispatcher)
        
    def start_minutes(self, stanza):
        """Starts minutes"""
        self.conversation.transfer(self.minuteman_dispatcher)

class MinutemanDispatcher(basic.Dispatcher):
    """Minutes taking dispatcher"""
    def __init__(self, conversation, main_dispatcher):
        self.main_dispatcher = main_dispatcher
        self.minuteman = Minuteman(conversation.info)
        basic.Dispatcher.__init__(self,conversation)
        
    def dispatcher(self):
        """Options to take minutes"""
        return [
        ("Manage minutes", self.main_dispatcher.manage_minutes),
        ("I'm the scribe", self.minuteman.set_scribe),
        ("I am the scribe", self.minuteman.set_scribe),
        ("^Topic: (.*)", self.minuteman.add_topic),
        ("^Chair: (.*)", self.minuteman.set_chair),
        ("^Title: (.*)", self.minuteman.set_title),
        ("^Minutes info", self.minuteman.show_info),
        ("^To be minuted: (.+?): (.+)",self.minuteman.add_statement),
        ("\.\.\.(.*)", self.minuteman.continue_statement),
        ("Show minutes", self.minuteman.show_info),
        ("End minutes", self.minuteman.end_minutes)
        ]
  
class Minuteman(basic.Messenger):
    """Takes minutes"""
    def __init__(self, conversation_info):
        self.db_session = models.get_session()
        self.minutes = Minutes()
        basic.Messenger.__init__(self, conversation_info)

    def set_scribe(self, stanza):
        """Sets the scribe"""
        if self.minutes.scribe:
            return self.message(messages.scribe_already_set.render())
        self.minutes.scribe = stanza.get_from().resource
        self.db_session.save(self.minutes)
        return self.message(messages.field_set_to.render(field="Scribe", 
                                                         value=self.minutes.scribe))
    
    def set_chair(self, stanza, chair):
        """Sets the chair"""
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set the chair"))    
        self.minutes.chair = chair
        return self.message(messages.position_set_to.render(position="Chair",
                                                     name=self.minutes.chair))
    
    def set_title(self, stanza, title):
        """Sets the title"""
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set the title"))    
        self.minutes.title = title
        return self.message(messages.field_set_to.render(field="Title", 
                                                         value=self.minutes.title))  
        
    def add_topic(self, stanza, topic):
        """Adds a topic"""
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="set a topic"))    
        self.minutes.topics.append(Topic(topic))
        return self.message(messages.field_set_to.render(field="Topic", 
                                                         value=self.minutes.topics[-1].title))
    
    def is_sent_by_scribe(self, stanza):
        """Check if a message is sent by the scribe"""
        if stanza.get_from().resource == self.minutes.scribe:
            return True
        return False

    def show_info(self, stanza):
        """Shows what has been minuted"""
        return self.message(messages.show_minutes.render(minutes=self.minutes))

    def add_statement(self, stanza, author, statement):
        """Adds a statement to the minutes"""
        if not self.is_sent_by_scribe(stanza):
            return self.message(messages.only_scribe_can.render(action="add minutes"))
        if len(self.minutes.topics) == 0:
            return self.message(messages.no_topic_for_minute.render())
        self.minutes.topics[-1].statements.append(Statement(author, statement))
        return self.no_message()
    
    def continue_statement(self, stanza, statement):
        """Continues previous statement"""
        if not self.is_sent_by_scribe(stanza):
            return self.no_message()
        if len(self.minutes.topics) == 0:
            return self.message(messages.no_topic_for_minute.render())
        if len(self.minutes.topics[-1].statements) == 0:
            return self.message(messages.no_minute_to_continue.render())
        self.minutes.topics[-1].statements[-1].text += ("\n%s" %(statement))
        return self.no_message()

    def end_minutes(self, stanza):
        """Ends minutes and saves them"""
        if self.conversation_info.room_state:
            attendees = self.conversation_info.room_state.users.keys()
            for i in attendees:
                self.minutes.participants.append(Participant(i))
        self.db_session.commit()
        return self.end(messages.minutes_ended.render())
    

class MinutesManagerDispatcher(basic.Dispatcher):
    """Dispatcher for minutes managing"""
    def __init__(self, conversation, main_dispatcher):
        self.main_dispatcher = main_dispatcher
        self.minutes_manager = MinutesManager(conversation.info)
        basic.Dispatcher.__init__(self,conversation)

    def dispatcher(self):
        """Various options to manage minutes"""
        return [("Show minutes", self.minutes_manager.show_available_minutes),
                ("Select minutes", self.minutes_manager.select_minutes_to_show),
                ("Remove minutes", self.minutes_manager.select_minutes_to_remove),
                ("Start minutes", self.main_dispatcher.start_minutes)
                ]

class MinutesManager(basic.Messenger):
    """Manages minutes"""
    def __init__(self, conversation_info):
        self.db_session = models.get_session()
        basic.Messenger.__init__(self, conversation_info)

        
    def show_available_minutes(self, stanza):
        """Shows minutes in the system"""
        return self.message(messages.show_available_minutes.render(minutes_list=self.db_session.query(Minutes)))
    
    def select_minutes_to_show(self, stanza):
        """Selects minutes to show"""
        options = [(i.id, i.title) for i in self.db_session.query(Minutes)]
        return self.ask_multiple_choice_question(messages.available_minutes_are.render(), 
                                                 options, 
                                                 self.show_selected_minutes)
        
    def show_selected_minutes(self, id, title):
        """Shows the selected minutes"""                  
        return self.message(messages.show_minutes.render(minutes=self.db_session.query(Minutes).filter_by(id=id)[0]))
     
    def select_minutes_to_remove(self, stanza):
        """Selects minutes to be removed"""
        options = [(i.id, i.title) for i in self.db_session.query(Minutes)]
        return self.ask_multiple_choice_question(messages.select_minutes_to_remove.render(), 
                                                 options, 
                                                 self.remove_minutes)

    def remove_minutes(self, id, title):
        """Removes selected minutes"""
        try:
            self.db_session.delete(self.db_session.query(Minutes).filter_by(id=id)[0])
            self.db_session.commit()
        except:
            return self.message(messages.error_deleting.render(id=id))
        return self.message(messages.minutes_deleted.render(id=id))
    

if __name__=="__main__":
    core.Core("config.cfg").start()
    