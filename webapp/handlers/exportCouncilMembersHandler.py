#! python
import tornado.web
from baseHandler import BaseHandler
from webservice import exportService

class ExportCouncilMembersHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
    	self.finish() # export feature disabled. placed finish here to quickly get out
        fileName, partyIds = self.request.arguments.get('fileName',[''])[0], self.request.arguments.get('partyIds',[''])[0]
        self.set_header("Content-type", "text/CSV")
        self.set_header("content-disposition", "attachment; filename=" + fileName)

        self.write(exportService.councilMembersToCsv(partyIds))
        self.finish()   