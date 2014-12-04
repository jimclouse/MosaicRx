#! python
import tornado.web
from partyHandler import PartyHandler
from webservice import graphService

class CouncilLeadHandler(PartyHandler):
    @tornado.web.asynchronous
    def get(self, councilLeadId):
        partyId = graphService.getPartyId('cl', councilLeadId)
        PartyHandler.get(self, partyId)