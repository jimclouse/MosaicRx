#! python
import tornado.web
from baseHandler import BaseHandler
from webservice import graphService

class ContinentFilterHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        callback=self.request.arguments.get('callback',[''])[0]
        self.set_header("Content-type", "application/json")
        ret_val = "%s({type_data: %s});" % (callback, graphService.continentFilters)
        self.write(ret_val)
        self.finish()
        
class TypeFilterHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        callback=self.request.arguments.get('callback',[''])[0]
        resp = graphService.getFilterTypes()
        self.set_header("Content-type", "application/json")
        ret_val = "%s({type_data: %s});" % (callback, resp)
        self.write(ret_val)
        self.finish()