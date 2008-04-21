import simplejson
import urllib2
from jabbs import util, core, basic

import messages
util.jinja_messages_from_strings(messages)


class Search:
    """Search through yahoo! search api"""
    def __init__(self, terms, limit=5):
        """Makes a new search through yahoo! search api"""
        url = "http://search.yahooapis.com/WebSearchService/V1/webSearch?appid=yahoosoyyo&query=%s&output=json&results=%s" % (terms, limit)
        result = ""
        for l in urllib2.urlopen(url):
            result += l
        results = simplejson.loads(result)
        self.results = [Result(r["Title"], r["Url"], r["Summary"]) for r in results["ResultSet"]["Result"]]
        
            
class Result:
    """Single result from a search"""
    def __init__(self, title, url, description):
        self.title = title
        self.url = url
        self.description = description

class JabsearchDispatcher(basic.Dispatcher):
    """Dispatcher for jabsearch"""
    def dispatcher(self):
        """Will return to searchs of the form jabsearch anything"""
        return [("jabsearch (.+)", Jabsearch(self.conversation.info).search)]

class Jabsearch(basic.Messenger):
    """Creates a new search from the specified terms"""
    def search(self, stanza, terms):
        results = Search(terms)
        return self.message(messages.search_result.render(results=results.results))


if __name__ == "__main__":
    core.Core("config.cfg").start()
