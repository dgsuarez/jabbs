import web
from minuteman import models
from jinja import Environment, FileSystemLoader


urls = (
  '/(\d*)', 'index')

env = Environment(loader=FileSystemLoader('templates'))

class index:
    def GET(self, id):
        db_session = models.get_session()
        if id:
            m = db_session.query(models.Minutes).filter_by(id=id).first()
            if m:
                print env.get_template('minutesinfo.jinja').render(minutes=m)
            else:
                print "mal"
        else:
            print env.get_template('minuteslist.jinja').render(minutes=db_session.query(models.Minutes))

web.webapi.internalerror = web.debugerror
if __name__ == "__main__": 
    web.run(urls, globals(), web.reloader)