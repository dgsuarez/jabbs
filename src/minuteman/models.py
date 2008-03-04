from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, clear_mappers, relation, sessionmaker

class Minutes(object):
    def __init__(self, scribe="", chair="", title=""):
        self.scribe = scribe
        self.chair = chair
        self.title = title
    
    def __str__(self):
        return """\
Title: %s
Chair: %s
Scribe: %s 
    
Topics:
%s
    """ % (self.title, self.chair, self.scribe, "\n".join(i.__str__() for i in self.topics))
        

class Topic(object):
    def __init__(self, title):
        self.title = title
        
    def __str__(self):
        return "%s \n%s" % (self.title, "\n".join(i.__str__() for i in self.statements)) 


class Statement(object):
    def __init__(self, author, text):
        self.author = author
        self.text = text
        
    def __str__(self):
        return "%s: %s"  % (self.author, self.text)

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
    clear_mappers()
    mapper(Minutes, minutes_table, properties={
                                               "topics":relation(Topic, backref="minutes")
                                               })
    mapper(Topic, topics_table, properties={
                                            "statements":relation(Statement, backref="topics")
                                            })
    mapper(Statement, statements_table)
    
    return sessionmaker(bind=mysql_db, autoflush=True, transactional=True)()
    

if __name__ == "__main__":
    init()
    