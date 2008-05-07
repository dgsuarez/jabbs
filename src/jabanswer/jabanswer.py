import simplejson
import urllib2
import urllib

from jabbs import util, core, basic


class Questions:
    """Search through yahoo! answers api"""
    def __init__(self, terms, limit=5):
        """Makes a new search through yahoo! answers api"""
        terms = urllib.quote(terms)
        url = "http://answers.yahooapis.com/AnswersService/V1/questionSearch?appid=yahoosoyyo&query=%s&output=json&results=%s" % (terms, limit)
        result = ""
        for l in urllib2.urlopen(url):
            result += l
        results = simplejson.loads(result)
        self.results = [Question(r["Content"], r["ChosenAnswer"]) for r in results["all"]["questions"]]
        
            
class Question:
    """Single question"""
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        
        
class JabanswerDispatcher(basic.Dispatcher):
    """Dispatcher for jabanswer"""
    def dispatcher(self):
        """Will return to questions (ending in ?)"""
        return [("(.+)?", Jabanswer(self.conversation.info).ask)]


class Jabanswer(basic.Messenger):
    """Creates a new question from the specified terms"""
    def ask(self, stanza, terms):
        try:
            results = Questions(terms)
            r = """Did yo mean to ask about:
             %s?
            In that case, this answer may be helpful:
           %s
            """ % (results.results[0].question, results.results[0].answer)
            return self.message(r)
        except:
            return self.message("An error has ocurred. Try again in a few moments")


if __name__ == "__main__":
    core.Core("config.cfg").start()
