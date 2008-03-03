class NoMessage:
    """No message has been sent"""
    pass


class StanzaMessage:
    """Regular stanza"""
    def __init__(self, stanza):
        self.stanza = stanza


class EndMessage:
    """Ending message and a stanza"""
    def __init__(self, stanza):
        self.stanza = stanza
