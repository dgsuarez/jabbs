from jabbs import controller, core

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class Transferer(controller.Controller):
    def hola(self, stanza):
        self.name = stanza.get_body()[5:]
        return self.message("hi")

    def adios(self, stanza):
        self.conversation.transfer(controller.Controller())
        return self.message("bye "+self.name)

    def controller(self):
        return [("hola", self.hola), ("adios", self.adios)]


if __name__=="__main__":
    core.Core("botiboti@127.0.0.1", "b3rb3r3ch0", Transferer).start()