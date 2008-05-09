import itertools
import re

from jabbs import basic, core


class PoorDispatcher(basic.Dispatcher):
    """Dispatcher for poorboy"""
    def __init__(self, conversation):
        self.poor = PoorBoy(conversation.info)
        
    def dispatcher(self):
        """Patterns to match"""
        return [("I('m| am) (.*?) because of (.*)", self.poor.because_of),
                ("I remember (.*)", self.poor.i_remember),
                ("Do you remember (.*?)\?", self.poor.i_remember),
                ("(.*?) is (.*)", self.poor.something_is),
                ("(y|Y)ou('re| are) (.*)", self.poor.you_are),
                ("I('m| am) (.*)", self.poor.i_am),
                ("((H|h)i|(h|H)ello)", self.poor.hello),
                ("((B|b)ye)|((g|G)oodbye)", self.poor.bye),
                ("((y|Y)es|(N|n)o)", self.poor.yes_no),
                ("(.*)", self.poor.default)
                ]
        

class PoorBoy(basic.Messenger):
    """Small Eliza like AI"""
    
    def __init__(self, conversation_info):
        self.cont = 0
        basic.Messenger.__init__(self, conversation_info)    
    
    def because_of(self, stanza, _, arg1, arg2):
        self.cont += 1
        ops =  ["Are you %s often?" % arg1,
                "So %s makes you %s. Tell me more about it" % (arg2, arg1),
                "Why does %s make you %s?" % (arg2, arg1)
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def i_remember(self, stanza, arg1):
        self.cont += 1
        ops = ["%s, sure, I remember too" % arg1,
               "%s... that was a long time ago, wasn't it?" % arg1,
               "I don't recall %s, tell me more about it" % arg1
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def something_is(self, stanza, arg1, arg2):
        self.cont += 1
        ops = ["Why do you think %s is %s" % (arg1, arg2),
               "I'm pretty sure %s isn't %s" % (arg1, arg2),
               "No one had ever told me about %s" % arg1
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def you_are(self, stanza, _1, _2, arg1):
        self.cont += 1
        ops = ["Why do you think I am %s?" % arg1,
               "There's no way you can get away with calling me %s" % arg1,
               "%s... I don't know wether to be flattered or not" % arg1
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def i_am(self, stanza, _, arg1):
        self.cont += 1
        ops = ["Why do you think you are %s?" % arg1,
               "Being %s can be cool" % arg1,
               "You have a pretty interesting view of yourself. Tell me more about it"
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def yes_no(self, stanza, *args):
        self.cont += 1
        ops = ["Please be a little more explicit",
               "You can talk a bit more, I don't get paid by the hour"
               ]
        return self.message(ops[self.cont % len(ops)])
    
    def hello(self, stanza, *args):
        return self.message("Hi, tell me something")
    
    def bye(self, stanza, *args):
        """Ends the conversation"""
        return self.end("bye")

    def default(self, stanza, arg1):
        self.cont += 1
        ops = ["I don't know what you mean",
               "I can't grasp what you are saying",
               "Come on, let's change subjects"
               ]
        return self.message(ops[self.cont % len(ops)])
    
    
if __name__=="__main__":
    core.Core("config.cfg").start()