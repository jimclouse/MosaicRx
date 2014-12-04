#! python
import tornado.web
import json
from baseHandler import BaseHandler
from webservice import relationshipDetailService

class RelationshipDetailHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        callback=self.request.arguments.get('callback',[''])[0]
        nodeId=self.request.arguments.get('nodeId',[''])[0]
        relationType=self.request.arguments.get('type',[''])[0]
        resp = relationshipDetailService.getRelationshipDetail(nodeId,relationType)
        self.set_header("Content-type", "application/json")
        ret_val = "%s({res_data: %s});" % (callback, json.dumps(resp))
        self.write(ret_val)
        self.finish()