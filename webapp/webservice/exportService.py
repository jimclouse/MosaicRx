import graphService
import dataUtils
from operator import itemgetter
import datetime
import logging

logger = logging.getLogger('Mosaic.export')

def councilMembersToCsv(partyIds):
	def getMostRecentJob(isCurrent, dateIndex, reverse):
		filteredJobs = filter(lambda x: x[3] == isCurrent, jobs[long(partyId)])
		
		if len(filteredJobs) == 0: return ['', '', '']

		mostRecent = sorted(filteredJobs, key = lambda x: datetime.datetime(datetime.MINYEAR, 1, 1) if x[dateIndex] is None else x[dateIndex], reverse = reverse)[0]
		#Title|Employer|Date
		return [mostRecent[4], graphService.parties[mostRecent[0]][1], '' if mostRecent[dateIndex] is None else mostRecent[dateIndex].strftime("%Y-%m-%d")]

	content = '"Council Member Id","Name","Biography","Current Title","Current Employer","Current Start Date","Former Title","Former Employer","Former End Date"\n'
	jobs = getJobs(partyIds)
	biographies = getBiographies(partyIds)

	ids = partyIds.split(',')
	for partyId in ids:
		councilMemberDetail = graphService.parties[long(partyId)]
		#CouncilMemberId|Name|Biography|Current Job Info|Former Job Info
		values = [str(councilMemberDetail[3]), councilMemberDetail[1], biographies[long(partyId)]] + getMostRecentJob(1, 1, False) + getMostRecentJob(0, 2, True)
		index = 0
		while index < len(values):
			values[index] == formatSafeCsv(values[index])
			index += 1

		content += '"' + '","'.join(values) + '"\n'
	return content

def getBiographies(partyIds):
	sql = """SELECT P.PartyId, P.Biography
				from person P
				where P.PartyId in (PARTY_IDS);""".replace("PARTY_IDS", partyIds)

	rows = getRows(sql, partyIds)
	biographies = {}
	for r in rows:
		biographies[r[0]] = "" if r[1] == None else r[1]
	return biographies

def getJobs(partyIds):
	sql = """SELECT R.FromPartyId, R.ToPartyId, R.FromDate, R.ThruDate, E.IsCurrent, E.Title
				from partyrelationship R
				 inner join employment E on R.partyrelationshipid = E.partyrelationshipid
				where R.partyrelationshiptype = 'EmployeeOf'
				and R.frompartyid in (PARTY_IDS);""".replace("PARTY_IDS", partyIds)

	rows = getRows(sql, partyIds)
	jobs = {}
	for r in rows:
		if not jobs.has_key(r[0]):
			jobs[r[0]] = []
		
		jobs[r[0]].append([r[1], r[2], r[3], r[4], r[5]])
	return jobs

def getRows(sql, partyIds):
	try:
		conn = dataUtils.getMysqlConnection()
		cur = conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		cur.close()
		return rows
	except Exception as e:
		logger.error("query failed: " + sql)
		raise

def formatSafeCsv(value):
	return str(value).replace(',', ' ')
