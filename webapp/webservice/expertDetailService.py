import json
import dataUtils
import logging
import graphService

logger = logging.getLogger('Mosaic.expertDetail')

def fetch(partyId):
	sql = "select biography from person where partyid = " + partyId + ";"

	rows = dataUtils.fetchAll(sql)
	if rows == None or len(rows) == 0:
		print sql
		logger.warning("partyId " + partyId + " did not return a detail record from the database")		
		return {}

	if len(rows) > 1: 
		logger.warning("partyId " + partyId + " returned more than 1 row on the detail query")

	partyDetail = graphService.getPartyDetails(long(partyId))
	if len(partyDetail) == 0: return {}

	name = partyDetail[1]
	sourceId = partyDetail[3]
	biography = rows[0][0]

	jobHistory = graphService.generateJobHistory(long(partyId))
	
	return {"name": name, "bio": biography, "jobHistory": jobHistory , "sourceId": sourceId}

def getDetail(partyId):
	return fetch(partyId)