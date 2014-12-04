#! python
import tornado.web
import json
from webservice import searchService
from baseHandler import BaseHandler

class CompanySearchHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        callback=self.request.arguments.get('callback', [''])[0]
        name_contains=self.request.arguments.get('name_contains',[''])[0]
        ret_val = searchService.searchCompanies(name_contains)
        self.send_response(callback, json.dumps(ret_val))

    def send_response(self, callback, resp):
        self.set_header("Content-type", "application/json")
        ret_val = "%s({res_data: %s});" % (callback, resp)
        self.write(ret_val)
        self.finish()