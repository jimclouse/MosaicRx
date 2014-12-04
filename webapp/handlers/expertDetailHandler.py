#! python
import tornado.web
import json
from webservice import expertDetailService
from baseHandler import BaseHandler

class ExpertDetailHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, expertId):
        callback=self.request.arguments.get('callback', [''])[0]
        ret_val = expertDetailService.getDetail(expertId)
        self.send_response(callback, json.dumps(ret_val))

    def send_response(self, callback, resp):
        self.set_header("Content-type", "application/json")
        ret_val = "%s({res_data: %s});" % (callback, resp)
        self.write(ret_val)
        self.finish()