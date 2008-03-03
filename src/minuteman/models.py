from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, relation

class Minutes(object):
    def __init__(self, scribe="", chair="", title=""):
        self.scribe = scribe
        self.chair = chair
        self.title = title
        

class Topic(object):
    def __init__(self, title):
        self.title = title


class Statement(object):
    def __init__(self, author, text):
        self.author = author
        self.text = text

def init():
    mysql_db = create_engine('mysql://minuteman:b3rb3r3ch0@127.0.0.1/minutes')
    metadata = MetaData()
    minutes_table = Table("minutes", metadata,
                          Column("id", Integer, primary_key=True),
                          Column("chair", String(100)),
                          Column("scribe", String(100)),
                          Column("title", String(200))
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
    
    metadata.create_all(mysql_db)
    mapper(Minutes, minutes_table, properties={
                                               "topics":relation(Topic, backref="minutes")
                                               })
    mapper(Topic, topics_table, properties={
                                            "statements":relation(Statement, backref="topics")
                                            })
    mapper(Statement, statements_table)
    
    

if __name__ == "__main__":
    init()
    
    