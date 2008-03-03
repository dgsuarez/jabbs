from jabbs import controller, core

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class PoorBoy(controller.Controller):
    
    def controller(self):
        return [("^bye", self.bye),
                (".*", self.change_person)]
    
    def change_person(self, stanza):
        substitutions = [("you", "i"),
                     ("are", "am"),
                     ("me","you"),
                     ("am", "are"),
                     ("i", "you"),
                     ("you're", "i'm"),
                     ("i'm", "you're"),
                     ("your", "my"),
                     ("my", "your")
                     ]
        body = stanza.get_body()
        s_body = [[word, False] for word in body.split()]
        
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
    core.Core("botiboti@127.0.0.1", "b3rb3r3ch0", PoorBoy).start()