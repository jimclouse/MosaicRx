#! python
import tornado.web
from partyHandler import PartyHandler
from webservice import graphService

class CouncilApplicantHandler(PartyHandler):
    @tornado.web.asynchronous
    def get(self, councilApplicantId):
        partyId = graphService.getPartyId('ca', councilApplicantId)
        PartyHandler.get(self, partyId)