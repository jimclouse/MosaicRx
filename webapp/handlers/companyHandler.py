#! python
import tornado.web
from partyHandler import PartyHandler
from webservice import graphService

class CompanyHandler(PartyHandler):
    @tornado.web.asynchronous
    def get(self, companyId):
        partyId = graphService.getPartyId('co', companyId)
        PartyHandler.get(self, partyId)