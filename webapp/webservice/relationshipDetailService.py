import json
import dataUtils
import utils
from decimal import *
from operator import itemgetter
import logging

revenuePct = {}

logger = logging.getLogger('Mosaic.relationship')

def init(partyDict):
	global revenuePct
	sql = "select fromPartyId, toPartyId, revenuePercent from partyrelationship where revenuePercent is not null and partyrelationshiptype = 'CustomerOf';"
	# alcoa, alumina, 37%, customerOf alcoal is a customer of alumina and it gets 37% of its revenue from alumina

	# alcoa is a customer of alumina and alumina get s37% of rev from alcoa 
	fileName = "cache/relationshipRevenue.tmp"
	logger.info("loading revenue percentages")
	rows = dataUtils.loadCachableData(fileName,sql)

	for item in rows:
		fromPartyId, toPartyId, revenue_percent = item[1], item[0], round(Decimal(item[2],2))

		if partyDict.has_key(toPartyId):
			toPartyName = partyDict[toPartyId][1]
			
			if not revenuePct.has_key(fromPartyId):
				revenuePct[fromPartyId] = []

			existing = filter(lambda x: utils.normalizeName(x["name"]) == utils.normalizeName(toPartyName), revenuePct[fromPartyId])
			#existing = [x for item in revenuePct[fromPartyId] if x["name"] = toPartyName]
			if len(existing) == 0:
				revenuePct[fromPartyId].append({"name": toPartyName ,"id": toPartyId, "value": revenue_percent})
			


def getRevenuePercent(nodeId):
	nodeId = int(nodeId)
	if not revenuePct.has_key(nodeId): return []
	revenueList = revenuePct[nodeId] 
	revenueTotal = 0.0

	revenueList = sorted(revenueList, key=itemgetter("value"), reverse=True)
	if len(revenueList) > 9:
		revenueList = revenueList[:9]

	revenueTotal = sum([x["value"] for x in revenueList])
	if revenueTotal < 100:
		revenueList.append({"name": "Other", "value": (100 - revenueTotal) })

	# one more sort to make sure Other is in the right spot
	revenueList = sorted(revenueList, key=itemgetter("value"), reverse=True)

	return revenueList


def getRelationshipDetail(nodeId,type):
	if type == "Customers":
		return getRevenuePercent(nodeId)

	# return sample data
	return { "company1": { "value": 11.4, "id": 6442462449}, "company2": { "id": 6442930949, "value": 20.5}, "company3": {"value": 5.1, "id": 6442800558},
	"Other": {"value": 50 } }