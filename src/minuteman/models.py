from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

class Minutes:
    def __init__(self, scribe="", chair="", title=""):
        self.scribe = scribe
        self.chair = chair
        self.title = title
        

class Topic:
    def __init__(self, title):
        self.title = title


class Statement:
    def __init__(self, author, text):
        self.author = author
        self.text = text

def init():
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
                         )
    statements_table = Table("", metadata,
                             Column("id", Integer, primary_key=True),
                             Column("author", String(100)),
                             Column("statement", String(500))
                             )
    
    