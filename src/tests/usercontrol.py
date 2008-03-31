from jabbs import basic, core

class Dispatcher(basic.Dispatcher):
    def dispatcher(self):
        return [(".+", Messenger(self.conversation.info).say)]
                 

class Messenger(basic.Messenger):
    def say(self, stanza):
        return self.message("good")


class UserControl:
    def user_control(self, user):
        user_str = "%s@%s" % (user.node, user.domain)
        return user_str in ["gramparsons@127.0.0.1"]
    
if __name__ == "__main__":
    core.Core("usercontrol.cfg").start()