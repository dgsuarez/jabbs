class NoMessage:
    """No message has been sent"""
    pass


class UserConnected:
    """A user has started his session"""
    pass


class UserDisconnected:
    """A user has ended his session"""
    pass


class StanzaMessage:
    """Regular stanza"""
    def __init__(self, stanza):
        self.stanza = stanza


class EndMessage(StanzaMessage):
    """Ending message and a stanza"""


class Question:
    """Base class for question messages: Question to be asked and callback function
    to be called with the answer
    """
    def __init__(self, question, callback):
        self.question = question
        self.callback = callback


class YesNoQuestion(Question):
    """Yes/no question to be asked and a callback function which receives True
    (yes) or False (no)
    """
    pass


class MultipleChoiceQuestion(Question):
    """Multiple choice question: The question, the options and a callback 
    function
    """
    def __init__(self, question, options, callback):
        self.question = question
        self.options = options
        self.callback = callback
