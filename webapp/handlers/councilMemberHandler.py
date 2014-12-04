#! python
import tornado.web
from partyHandler import PartyHandler
from webservice import graphService

class CouncilMemberHandler(PartyHandler):
    @tornado.web.asynchronous
    def get(self, councilMemberId):
        partyId = graphService.getPartyId('cm', councilMemberId)
        PartyHandler.get(self, partyId)