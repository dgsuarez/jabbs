import itertools

from jabbs import basic, core


class PoorDispatcher(basic.Dispatcher):
    def __init__(self, conversation):
        self.poor = PoorBoy(conversation.info)
        
    def dispatcher(self):
        return [("^bye", self.poor.bye),
                ("(.*)", self.poor.get_answer)]
        
class PoorBoy(basic.Messenger):
    
    def get_answer(self, stanza, body):
        a = self.is_greeting(body)
        if a:
            return self.message(a)
        a = self.ask_about_parents(body)
        if a:
            return self.message(a)
        return self.message(self.ask_about(body))

    def is_greeting(self, body):
        greetings = ("hi", "hello")
        for i in greetings:
            if i in body:
                return "Hi"
        return False 
    
    def ask_about_parents(self, body):
        mother = ("mother", "mom", "mommy")
        father = ("father", "dad", "daddy")
        for i in itertools.chain(mother, father):
            if i in body:
                return "What about your %s" % i
        return False
    
    def ask_about(self, body):
        substitutions = [("you", "I"),
                     ("are", "am"),
                     ("me","you"),
                     ("am", "are"),
                     ("i", "you"),
                     ("you're", "I'm"),
                     ("i'm", "you're"),
                     ("your", "my"),
                     ("my", "your")
                     ]
        s_body = [[word.lower(), False] for word in body.split()]
        if s_body[0][0] == "because":
            s_body = s_body[1:]
        for o, n in substitutions:
            for l in s_body:
                if o == l[0] and not l[1]:
                    l[0]=n
                    l[1]=True
        body = " ".join([l[0] for l in s_body])
        return "Tell me more about why %s" % body
    
    def bye(self, stanza):
        return self.end("bye")

if __name__=="__main__":
    core.Core("config.cfg").start()