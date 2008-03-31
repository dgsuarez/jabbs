from jabbs import core, basic

class Dispatcher(basic.Dispatcher):
    
    def dispatcher(self):
        return [("(.*)", Echo(self.conversation.info).echo)]
    
class Echo(basic.Messenger):
    def echo(self, stanza, text):
        return self.message(text)


if __name__=="__main__":
    core.Core("echo.cfg").start()