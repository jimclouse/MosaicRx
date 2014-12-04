#! python
import tornado.web
import json
from webservice import graphService
from baseHandler import BaseHandler

class PartyHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, partyId):
        callback=self.request.arguments.get('callback',[''])[0]
        self.request.arguments.pop('callback')
        self.request.arguments.pop('_')
        ret_val = graphService.getJson(partyId, self.request.arguments)
        self.send_response(callback, json.dumps(ret_val))

    def send_response(self, callback, resp):
        self.set_header("Content-type", "application/json")
        ret_val = "%s({res_data: %s});" % (callback, resp)
        self.write(ret_val)
        self.finish()