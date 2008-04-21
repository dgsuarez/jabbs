from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey
from sqlalchemy.orm import mapper, clear_mappers, relation, sessionmaker



class Minutes(object):
    """Represents minutes"""
    def __init__(self, scribe="", chair="", title="No title"):
        self.scribe = scribe
        self.chair = chair
        self.title = title
        self.date = datetime.now()
    
    def __str__(self):
        return """\
Title: %s
Chair: %s
Scribe: %s 

Participants: %s
Topics:
%s
    """ % (self.title, 
           self.chair, 
           self.scribe,
           ",".join(i.__str__() for i in self.participants),
           "\n".join(i.__str__() for i in self.topics))
        

class Topic(object):
    """A topic in minutes"""
    def __init__(self, title):
        self.title = title
        
    def __str__(self):
        return "%s \n%s" % (self.title, "\n".join(i.__str__() for i in self.statements)) 


class Statement(object):
    """A statement in a topic"""
    def __init__(self, author, text):
        self.author = author
        self.text = text
        
    def __str__(self):
        return "%s: %s"  % (self.author, self.text)


class Participant(object):
    """Participant in minutes"""
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name

def init():
    """Creates a connection to the db and sets the mappings"""
    mysql_db = create_engine('mysql://minuteman:b3rb3r3ch0@127.0.0.1/minutes')
    metadata = MetaData()
    minutes_table = Table("minutes", metadata,
                          Column("id", Integer, primary_key=True),
                          Column("chair", String(100)),
                          Column("scribe", String(100)),
                          Column("title", String(200)),
                          Column("date", DateTime)
                          )
    topics_table = Table("topics", metadata,
                         Column("id", Integer, primary_key=True),
                         Column("title", String(200)),
                         Column('minutes_id', Integer, ForeignKey('minutes.id'))
                         )
    statements_table = Table("statements", metadata,
                             Column("id", Integer, primary_key=True),
                             Column("author", String(100)),
                             Column("text", String(500)),
                             Column('topics_id', Integer, ForeignKey('topics.id'))
                             )
    participants_table = Table("participants", metadata,
                               Column("name", String(200), primary_key=True),
                               Column('minutes_id', Integer, ForeignKey('minutes.id'))
                               )
    metadata.create_all(mysql_db)
    clear_mappers()
    mapper(Minutes, minutes_table, properties={
                                               "topics":relation(Topic, backref="minutes"),
                                               "participants":relation(Participant, backref="participants")
                                               })
    mapper(Topic, topics_table, properties={
                                            "statements":relation(Statement, backref="topics")
                                            })
    mapper(Statement, statements_table)
    mapper(Participant, participants_table)
    
    return sessionmaker(bind=mysql_db, autoflush=True, transactional=True)
    
def get_session():
    """Returns the db session"""
    return session()
    
session = init()