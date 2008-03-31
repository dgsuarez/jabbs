from jabbs import core, basic

class Dispatcher(basic.Dispatcher):
    
    def __init__(self, conversation):
        self.asker = Asker(conversation.info)
    
    def dispatcher(self):
        return [("regular", self.asker.regular),
                ("yesno", self.asker.yesno),
                ("choice", self.asker.choice)
                ]
    
class Asker(basic.Messenger):
    
    def regular(self, stanza):
        return self.ask_question("Is it correct?", self.regular_callback)
    
    def regular_callback(self, answer):
        if answer == "yes":
            return self.message("good")
        return self.message("bad")
    
    def yesno(self, stanza):
        return self.ask_yes_no_question("Is it correct?", self.yesno_callback)
    
    def yesno_callback(self, is_correct):
        if is_correct:
            return self.message("good")
        return self.message("bad")
    
    def choice(self, stanza):
        return self.ask_multiple_choice_question("Is it correct?", 
                                                 [(1, "yes"),(2, "no")], 
                                                 self.choice_callback)
    
    def choice_callback(self, id, answer):
        if id == 1 and answer == "yes":
            return self.message("good")
        return self.message("bad")
    
if __name__=="__main__":
    core.Core("asker.cfg").start()