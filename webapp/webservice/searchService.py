#! python
import json
import dataUtils
import os
import time
import logging
from operator import itemgetter

logger = logging.getLogger('Mosaic.search')

companySearchCache = []
peopleSearchCache = []

def load():
	global companySearchCache

	logger.info("Starting company search indexing")
	start_time = time.time()

	fileName = "cache/companysearch.tmp"
	
	sql = """SELECT o.partyid, o.name, o.tickersymbol, o.stockexchange 
			from organization o 
			left join partyrelationship p on o.partyid = p.topartyid
			where o.companyid is not null
			group by o.partyid, o.name, o.tickersymbol, o.stockexchange
			order by count(*) desc;"""

	rows = dataUtils.loadCachableData(fileName,sql)

	for r in rows:
		partyid, partyName, normalizedPartyName, tickerSymbol, stockExchange = r[0], r[1], normalize(r[1]), r[2], r[3]

		companySearchCache.append([partyid, partyName, normalizedPartyName, tickerSymbol, stockExchange])

	logger.info(str(len(companySearchCache)) + " companies loaded into search in " + str(time.time() - start_time) + " seconds.")

	logger.info("Starting people search indexing")
	start_time = time.time()

	fileName = "cache/peoplesearch.tmp"
	
	sql = """SELECT p.partyid, 
					concat(p.firstname, ' ', p.lastname) as name,
					case   when councilmemberid is not null then 'cm' 
                            when councilleadid is not null then 'cl' 
                            when councilapplicantid is not null then 'ca'
                            end as partyType,
                    e.title,
                    o.name as company
            from person p
			left join partyrelationship r on p.partyid = r.topartyid
			inner join partyrelationship r2 on p.partyid = r2.frompartyid
				and r2.partyrelationshiptype = 'EmployeeOf'
			inner join organization o on r2.topartyid = o.partyid
			inner join employment e on e.partyrelationshipid = r2.partyrelationshipid
				and e.isprimary = 1
			where (p.councilmemberid > 0 
			or p.councilleadid > 0 
			or p.councilapplicantid > 0) 
			group by p.partyid, name, partyType, councilmemberid, councilleadid, councilapplicantid, title, company
			order by case   when councilmemberid is not null then 1
                            when councilleadid is not null then 3
                            when councilapplicantid is not null then 2
                            end asc, count(*) desc, name;"""

	rows = dataUtils.loadCachableData(fileName,sql)

	for r in rows:
		if r[1] is None: continue
		partyid, partyName, normalizedPartyName, partyType, title, company = r[0], r[1], normalize(r[1]), r[2], ("" if r[3] == None else r[3]), ("" if r[4] == None else r[4])

		peopleSearchCache.append([partyid, partyName, normalizedPartyName, partyType, title, company])

	logger.info(str(len(peopleSearchCache)) + " people loaded into search in " + str(time.time() - start_time) + " seconds.")

def searchCompanies(input):
	input = input.lower().encode("utf8")

	return filter(lambda x: (input in x[2]) or (not x[3] == None and input in x[3].lower()), companySearchCache)[0:10]

def searchPeople(input):
	input = input.lower().encode("utf8")

	return filter(lambda x: input in x[2], peopleSearchCache)[0:10]

def normalize(str):
	return str.lower().strip()







