import base

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class Transferer(base.Controller):
    def hola(self, stanza):
        print "en hola"
        self.name =  stanza.get_body()[5:]
        return self.message("hi")

    def adios(self, stanza):
        print "en adios"
        self.conversation.transfer(base.Controller(self.conversation))
        return self.message("bye "+self.name)

    def controller(self):
        print "en controller"
        return [("hola", self.hola), ("adios", self.adios)]


if __name__=="__main__":
    base.Core("botiboti@127.0.0.1", "b3rb3r3ch0", Transferer).start()
