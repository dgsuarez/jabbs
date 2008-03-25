import simplejson
import urllib2
from jabbs import util, core, controller

import messages
util.jinja_messages_from_strings(messages)


class Search:
    
    def __init__(self, terms, limit=5):
        url = "http://search.yahooapis.com/WebSearchService/V1/webSearch?appid=yahoosoyyo&query=%s&output=json&results=%s" % (terms, limit)
        result = ""
        for l in urllib2.urlopen(url):
            result += l
        results = simplejson.loads(result)
        self.results = []
        for r in results["ResultSet"]["Result"]:
            self.results.append(Result(r["Title"], r["Url"], r["Summary"]))
            
class Result:
    
    def __init__(self, title, url, description):
        self.title = title
        self.url = url
        self.description = description

class Jabsearch(controller.Controller):
    
    def controller(self):
        return [("jabsearch (.+)", self.search)]
    
    def search(self, stanza, terms):
        results = Search(terms)
        return self.message(messages.search_result.render(results=results.results))

if __name__ == "__main__":
    core.Core("config.cfg").start()
