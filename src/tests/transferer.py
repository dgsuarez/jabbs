from jabbs import basic, core
import echo

class Dispatcher(basic.Dispatcher):
    
    def __init__(self, conversation):
        self.trans = Transferer(conversation.info)
        basic.Dispatcher.__init__(self, conversation)
    
    def adios(self, stanza):
        self.conversation.transfer(echo.Dispatcher(self.conversation))
        return self.trans.adios(stanza)
    
    def dispatcher(self):
        return [("hola (.+)", self.trans.hola), ("adios", self.adios)] 

class Transferer(basic.Messenger):
    def hola(self, stanza, name):
        self.name = name
        return self.message("hi")

    def adios(self, stanza):
        return self.message("bye "+self.name)


if __name__=="__main__":
    core.Core("transferer.cfg").start()