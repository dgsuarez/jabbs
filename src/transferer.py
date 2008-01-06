import base

from pyxmpp.all import JID,Iq,Presence,Message,StreamError

class Transferer():
    def hola(self, stanza):
        self.name =  stanza.get_body()[5:]
        return Message(to_jid=stanza.get_from(), body="hi")

    def adios(self, stanza):
        self.__caller.transfer(base.Controller())
        return Message(to_jid=stanza.get_from(), body="bye "+self.name)

    def controller(self):
        return [("hola", self.hola), ("adios", self.adios)]

    def set_caller(self, caller):
        self.__caller=caller

if __name__=="__main__":
    base.Core("botiboti@127.0.0.1", "b3rb3r3ch0", Transferer()).start()
