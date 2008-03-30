import jinja
import types
import basic


def jinja_messages_from_strings(obj):
    """Converts all strings in a module or object into jinja templates"""
    env = jinja.Environment()
    for message in dir(obj):
        if type(getattr(obj, message)) == types.StringType and message[0] != "_":
            setattr(obj, message, env.from_string(getattr(obj,message)))
            
