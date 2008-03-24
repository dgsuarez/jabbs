import jinja
import types

def controller_from_bot_methods(controller):
        """Takes all methods of the instance in the form bot_* and returns
        a controller list in the form [(regex matching the name of the
        method without bot_, method)]

        """
        botregex = re.compile(r"^bot_.+")
        botmethods = [method for method in dir(controller) 
                                    if callable(getattr(controller,method))
                                       and botregex.match(method)]
        regexes = ["^"+method[4:]+".*" for method in botmethods]
        return zip(regexes, [getattr(controller, method) for method in botmethods])

def messages_from_string(obj):
    """Converts all strings in a module or object into jinja templates"""
    env = jinja.Environment()
    for message in dir(obj):
        if type(getattr(obj, message)) == types.StringType and message[0] != "_":
            print message, type(message), getattr(obj,message), message.__class__
            setattr(obj, message, env.from_string(getattr(obj,message)))
            
