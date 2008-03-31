from jabbs import core, basic

class Dispatcher(basic.Dispatcher):
    
    def __init__(self, conversation):
        self.counter = Counter(conversation.info)
    
    def dispatcher(self):
        return [("bye", self.counter.bye),
                (".*", self.counter.next)
                ]
        
class Counter(basic.Messenger):
    
    def __init__(self, info):
        self.count = 0
        basic.Messenger.__init__(self, info)
        
    def next(self, stanza):
        self.count +=1
        return self.message("%d" % self.count)
    
    def bye(self, stanza):
        return self.end("bye")
    
if __name__=="__main__":
    core.Core("counter.cfg").start()