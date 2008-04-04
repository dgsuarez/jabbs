import logging

class ParseError(Exception):
    pass

class Config:
    
    def __init__(self, path):
        """Parses a config file with python dictionary format"""
        logger = logging.getLogger("logger")
        f =  open(path)
        c = "".join(open(path).readlines())
        f.close()
        conf =  eval(c)
        try:
            self.jid = conf["jid"]
            self.password = conf["password"]
        except:
            logger.error("JID and password must be provided in configuration file")
            raise ParseError
        module, modclass = self.__read_starter(conf, logger)
        self.starter_params = conf.get("starter params", {})
        self.__read_user_control(conf)
        self.nick = conf.get("nick", "botiboti")
        self.rooms_to_join = conf.get("rooms to join", [])
        self.start_on_user_connect = conf.get("start on user connect", None)
        if self.start_on_user_connect == "yes":
            self.start_on_user_connect = True
        else:
            self.start_on_user_connect = False

    def __read_starter(self, conf, logger):
        try:
            self.starter_str = conf["starter"]
            modclass = self.starter_str.rsplit(".", 1)
            module = __import__(modclass[0])
            self.starter = getattr(module, modclass[1])
        except:
            logger.error("Valid starter dispatcher must be provided in configuration file")
            raise ParseError
        return module, modclass

    def __read_user_control(self, conf):
        user_control_str =  conf.get("user control", None)
        if not user_control_str:
            self.user_control = lambda x: True
        else:
            modclassfun = user_control_str.rsplit(".",2)
            module = __import__(modclassfun[0])
            class_ = getattr(module, modclassfun[1])
            self.user_control = class_().user_control 

