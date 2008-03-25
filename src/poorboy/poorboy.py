from jabbs import controller, core

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class PoorBoy(controller.Controller):
    
    def controller(self):
        return [("^bye", self.bye),
                ("(.*)", self.change_person)]
    
    def change_person(self, stanza, body):
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
        
        for o, n in substitutions:
            for l in s_body:
                if o == l[0] and not l[1]:
                    l[0]=n
                    l[1]=True
        body = " ".join([l[0] for l in s_body])
        return self.message("I know " + body)
    
    def bye(self, stanza):
        return self.end("bye")

if __name__=="__main__":
    core.Core("config.cfg").start()