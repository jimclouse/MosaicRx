#! python
# -*- coding: utf-8 -*-
import json
from operator import itemgetter
import os
import time
import datetime
import dataUtils
import utils
import logging
import relationshipDetailService
import memcache
from datetime import date
from dateutil.relativedelta import relativedelta

# output dictionaries
graph = {}
parties = {}
jobs = {}
physicalAddresses = {}
leadsApplicants = {}
orgsWithCMs = []

max_time = datetime.datetime(datetime.MAXYEAR, 1, 1)
min_time = datetime.datetime(datetime.MINYEAR, 1, 1)

# create memcache connection
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#initialize logger
logger = logging.getLogger('Mosaic.graph')

cacheFile_loc = "./cache"

itemTypeMap = {"g" : "partygroup", "o" : "organization", "cl" : "client", "co" : "company", "p" : "person", 
                "cm" : "councilmember", "cn" : "contact", "ca": "applicant", "cl": "lead"}

relationshipTypeFilters = [{"columnName": "SupplierOf", "filterName" : "Suppliers", "fromDisplayName" : "Suppliers", "toDisplayName" : "Supplier To"},
                            {"columnName": "CompetitorOf", "filterName" : "Competitors", "fromDisplayName" : "Competitors", "toDisplayName" : "Competitors"},
                            {"columnName": "DistributorOf", "filterName" : "Distributors", "fromDisplayName" : "Distributors", "toDisplayName" : "Distributor For"},
                            {"columnName": "JointVentureWith", "filterName" : "Joint Ventures", "fromDisplayName" : "Joint Ventures", "toDisplayName" : "Joint Ventures"},
                            {"columnName": "CustomerOf", "filterName" : "Customers", "fromDisplayName" : "Customers", "toDisplayName" : "Customer Of"},
                            {"columnName": "ParentOf", "filterName" : "Organization Hierarchy", "fromDisplayName" : "Parents", "toDisplayName" : "Subsidiaries"},
                            {"columnName": "MemberOf", "filterName" : "Members", "fromDisplayName" : "Members", "toDisplayName" : "Membership"},
                            {"columnName": "LeadFor", "filterName" : "Leads", "fromDisplayName" : "Leads", "toDisplayName" : "Lead For"},
                            {"columnName": "EmployeeOf", "filterName" : "Employment (Former)", "fromDisplayName" : "Former Employees", "toDisplayName" : "Former Employer"},
                            {"columnName": "EmployeeOf", "filterName" : "Employment (Current)", "fromDisplayName" : "Current Employees", "toDisplayName" : "Current Employer"}
                            ]

continentFilters = []

################
# Sql statements

Sql_LeadsApplicants = """SELECT pr.FromPartyId
                            ,pr.PartyRelationshipType
                            ,pr.fromDate
                            ,pr.thruDate
                    from partyRelationship pr
                    where pr.partyrelationshiptype in ('LeadFor', 'ApplicantTo');"""

Sql_PhysicalAddress = """SELECT a.partyid
                            ,a.continent
                    from physicaladdress a
                    where a.isprimary = 1;"""


Sql_PartyGroups = """SELECT g.partyid
                            ,'g' as partyType
                            ,g.name
                            ,count(*) as connections 
                            ,g.partygrouptype
                    from partygroup g
                    left join partyrelationship pr on g.partyid = pr.topartyid 
                    group by g.partyid, g.name, g.partygrouptype;"""

Sql_People = """SELECT p.partyid
                    ,case   when councilmemberid is not null then 'cm' 
                            when contactid is not null then 'cn' 
                            when councilleadid is not null then 'cl' 
                            when councilapplicantid is not null then 'ca'
                            else 'p' end as partyType
                    ,concat(p.firstname, ' ', p.lastname) as name
                    ,count(*) as connections
                    ,coalesce(councilmemberid, contactid, councilleadid, councilapplicantid) as sourceid 
                    ,p.IsDnc
                    ,P.IsMemberPrograms
                    ,p.IsTermsAndConditionsSigned
                from person p left join partyrelationship pr on p.partyid = pr.topartyid 
                where (p.councilmemberid is not null or p.councilleadid is not null or p.councilapplicantid is not null)
                and p.firstname is not null and p.lastname is not null
                group by p.partyid
                    , concat(p.firstname, ' ', p.lastname)
                    , partytype
                    , sourceid,p.IsDnc
                    ,P.IsMemberPrograms
                    ,p.IsTermsAndConditionsSigned
                having name is not null;"""

Sql_Organizations = """SELECT p.partyid
                            ,case when companyid is not null then 'co' when clientid is not null then 'cl' else 'o' end as partyType
                            ,p.name
                            ,count(*) as connections
                            ,coalesce(companyid, clientid) as sourceid
                            ,p.TickerSymbol
                            ,p.StockExchange
                            ,p.IsDNC
                        from organization p 
                            left join partyrelationship pr on p.partyid = pr.topartyid
                        where clientid is null 
                        group by p.partyid, p.name, partytype, sourceid, p.tickerSymbol, p.stockExchange,p.IsDNC;"""

Sql_JobRecords = """SELECT r.frompartyid
                        ,e.title
                        ,o.name
                        ,r.topartyid
                    from partyrelationship r 
                        inner join employment e on r.partyrelationshipid = e.partyrelationshipid
                        inner join organization o on r.topartyid = o.partyid
                        where e.isCurrent = 1;"""

Sql_Continents = """SELECT distinct p.continent
                    from physicaladdress p where p.continent is not null;"""

Sql_OrganizationsWithCMs = """SELECT O.PartyId
                                FROM Organization O
                            WHERE EXISTS (SELECT 1 FROM PartyRelationship R INNER JOIN Person P ON R.FromPartyId = P.PartyId WHERE P.IsTermsAndConditionsSigned = 1 AND O.PartyId = R.ToPartyId);"""

def getPartyDetails(partyId):
    if not parties.has_key(partyId):
        return {}
    return parties[partyId]

def getPartyId(partyType, sourceId):
    try:
        sourceId = long(sourceId)
    except (ValueError):
        return None

    d = [k for (k,v) in parties.iteritems() if v[0] == partyType and v[3] == sourceId]

    return None if len(d) == 0 else d[0]


def getJson(partyId, filters):
    global mc

    if partyId == None: return {}

    # check if in cache with the particular current filter
    filterString = str(filters)
    cachedItem = mc.get(str(partyId)) # for memcached, key must be string both on set and get
    if ( not cachedItem == None ) and (cachedItem['filters'] == utils.checksum(filterString)):
        return cachedItem['graph']
    else:
        graph = loadGraph(partyId, filters)
        mc.set(str(partyId), {'filters': utils.checksum(filterString), 'graph': graph }, 60)
        return graph

def buildFormerEmployementDateFilter(pFilter):
    sql = " and (e.iscurrent = 1 or e.iscurrent is null or (e.iscurrent = 0 and (pr.thrudate {FILTER}))) "
    if "FormerAllTime" in pFilter:
        return ""
    elif "FormerLast6" in pFilter:
        return sql.replace("{FILTER}", " < '" + (date.today().replace(day = 1) + relativedelta(months = -6)).isoformat() + "' or e.endyear < " + str(date.today().year - 1))
    elif "FormerLast12" in pFilter:
        return sql.replace("{FILTER}", " < '" + (date.today().replace(day = 1) + relativedelta(years = -1)).isoformat() + "' or e.endyear < " + str(date.today().year - 2))
    elif "FormerLast24" in pFilter:
        return sql.replace("{FILTER}", " < '" + (date.today().replace(day = 1) + relativedelta(years = -2)).isoformat() + "' or e.endyear < " + str(date.today().year - 3))
    elif "FormerUnknown" in pFilter:
        return sql.replace("{FILTER}", "is null")

def loadGraph(partyId, filters):
    global nodeDict
    global graph
    # limit types of relationships being displayed using user supplied filter
    try:
        uFilter = getFilterValue(filters, 'ufilter').split(",")
    except Exception as e:
        uFilter = getFilterTypes()
        print e

    fromTypeFilterQuery = buildTypeFilterQuery(uFilter)
    toTypeFilterQuery = buildTypeFilterQuery(uFilter,['Customers', 'Suppliers','Distributors'])

    formerEmployementDateFilter = buildFormerEmployementDateFilter(getFilterValue(filters, 'pFilter'))

    conn = dataUtils.getMysqlConnection()
    
    # root node
    iDict = createPartyNode(partyId, "root", None)

    sql = """SELECT distinct pr.frompartyId, pr.PartyRelationshipType, e.iscurrent, 1 as IsFrom, IsFromRevere, IsFromCreditSuisse
                from partyrelationship pr left join employment e on pr.PartyRelationshipId = e.PartyRelationshipId
                where pr.ToPartyId = %s  """ + fromTypeFilterQuery + formerEmployementDateFilter + """ UNION all 
                SELECT distinct pr.topartyId, pr.PartyRelationshipType, e.iscurrent, 0 as IsFrom, IsFromRevere, IsFromCreditSuisse
                from partyrelationship pr  left join employment e on pr.PartyRelationshipId = e.PartyRelationshipId
                where pr.FromPartyId = %s  """ + toTypeFilterQuery + ";"

    appendParties(conn, sql, iDict, filters)

    
    return iDict

def getFilterValue(filters, filterName):
    return filters.get(filterName, [''])[0]

def buildTypeFilterQuery(uFilter, exclusion=[]):
    if len(uFilter) == 0: return "" # get out if no types to filter on

    filters = filter(lambda x: x["filterName"] in uFilter and not x["filterName"] in exclusion , relationshipTypeFilters)

    filters = map(lambda x: x["columnName"], filters)

    return (" and pr.PartyRelationshipType in ('" + "','".join(filters) + "') ")

def getFilterTypes():
    filters = map(lambda x: x["filterName"], relationshipTypeFilters)
    return sorted(filters, key=itemgetter(0), reverse=False)

def subclassRelationshipType(relationshipType, isCurrent, isFrom):
    relationshipTypeFilter = None
    if isCurrent == 0:
        relationshipTypeFilter = filter(lambda x: x["filterName"] == "Employment (Former)", relationshipTypeFilters)[0]
    elif isCurrent == 1:
        relationshipTypeFilter = filter(lambda x: x["filterName"] == "Employment (Current)", relationshipTypeFilters)[0]
    else:
        relationshipTypeFilter = filter(lambda x: x["columnName"] == relationshipType, relationshipTypeFilters)[0]

    return relationshipTypeFilter["fromDisplayName"] if isFrom == 1 else relationshipTypeFilter["toDisplayName"]

def dateCoalesce(val, x):
    if not val is None: 
        return val
    if x == "min": 
        return min_time
    if x == "max":
        return max_time

def isViewableLeadApplicant(partyId, type):
    LEAD_APPLICANT_CUTOFF_YEARS = 2

    try:
        if not leadsApplicants.has_key(partyId): 
            return False

        detail = leadsApplicants[partyId]
        _relationshipType, _fromDate, _thruDate = detail[0], detail[1], detail[2]
        if _fromDate < datetime.datetime.now().replace(year = datetime.datetime.now().year-LEAD_APPLICANT_CUTOFF_YEARS):
            return False
        #if _thruDate is max_time:
        #    print "thru date fail"
        #    return False # a toDate indicates the lead or applicant has been denied or converted, etc.
        return True
    except Exception as e:
        logger.warn("lead applicant detail lookup failed. returned false and skipped individual in graph")
        return False


def appendParties(conn, sql, root, filters):
    cur = conn.cursor()
    cur.execute(sql, [root["id"], root["id"]])
    # fromPartyId | relationshipType | isCurrent | direction
    rows = cur.fetchall()
    cur.close()

    #1) Separate EmployeeOf into Former and Current based on IsCurrent flag
    #2) Add rank to each row
    #ItemId|RelationshipType|Rank
    employeeTypeFilters = filter(lambda x: x["filterName"] in getFilterValue(filters, 'ufilter'), relationshipTypeFilters)
    toFilters = map(lambda x: x["toDisplayName"], employeeTypeFilters)
    fromFilters = map(lambda x: x["fromDisplayName"], employeeTypeFilters)

    # remove any relationships where there is no corresponding party
    # because we only cache and display certain types of entities, but return the relationships for them, the ids will generate a 
    # key error if we try to pull the details
    newRows = filter(lambda x: parties.has_key(x[0]), rows) 
    newRows = filter(lambda x: x[1] in toFilters or x[1] in fromFilters, 
            ([item[0]] + [subclassRelationshipType(item[1], item[2], item[3])] + [parties[item[0]][2]] +  [item[4]] + [item[5]] for item in newRows))

    # convert nCt to integer

    try:
        GROUP_NODE_LIMIT = int(getFilterValue(filters, 'nCt'))
    except (TypeError, ValueError):
        GROUP_NODE_LIMIT = 10

    pFilter = getFilterValue(filters, 'pFilter')
    ctFilter = getFilterValue(filters, 'ctFilter')
    cmctFilter = getFilterValue(filters, 'cmctFilter')
    nFilter = getFilterValue(filters, 'nFilter')
    cFilter = getFilterValue(filters, 'cFilter')

    #Sort by rank
    newRows = sorted(newRows, key=itemgetter(2), reverse=True)
    for item in newRows:
        itemId = item[0]
        relationshipType = item[1]
        partyDetail = parties[itemId]
        itemType = itemTypeMap[partyDetail[0]]

        if itemType =="councilmember":
            isDnc, isMemberPrograms, signedTC, continent = partyDetail[4], partyDetail[5], partyDetail[6], physicalAddresses[itemId] if physicalAddresses.has_key(itemId) else ""
            if ((not "DoNotContact" in pFilter) and isDnc) or \
                (len(continent) > 0 and (not continent in cmctFilter)) or \
                ((not "MemberPrograms" in pFilter) and isMemberPrograms) or \
                ((not "NonMP" in pFilter) and (not isMemberPrograms)) or \
                (("ActiveCouncilMembers" in cFilter) and (not signedTC == 1)): continue
        elif itemType == "company":
            isDnc, isPublic, continent = partyDetail[6], (not partyDetail[4] == 0 and not partyDetail[4] == None), physicalAddresses[itemId]
            if (not "DoNotContact" in cFilter) and isDnc or \
                (len(continent) > 0 and (not continent in ctFilter)) or \
                ((not "Public" in cFilter) and isPublic) or \
                ((not "Private" in cFilter) and (not isPublic)) or \
                (("ActiveCouncilMembers" in cFilter) and (not long(itemId) in orgsWithCMs)): continue
        elif itemType == "organization" or itemType == "client":
            continent = physicalAddresses[itemId] if physicalAddresses.has_key(itemId) else ""
            if (len(continent) > 0 and (not continent in ctFilter)): continue
        elif itemType == "partygroup":
            if (not "DynamicStudyGroup" in nFilter and partyDetail[3] == "Dynamic Study Group") or \
                (not "StaticStudyGroup" in nFilter and partyDetail[3] == "Static Study Group"): continue
        elif itemType == "lead" or itemType  == "applicant":
            continent = physicalAddresses[itemId] if physicalAddresses.has_key(itemId) else ""
            if not isViewableLeadApplicant(itemId, itemType) or \
                ("ActiveCouncilMembers" in cFilter) or \
                (len(continent) > 0 and (not continent in cmctFilter)): continue

        # add groups as children    
        # add actual children to groups
        group = filter(lambda x: x["name"] == relationshipType, root["children"])
        if group == []:
            hasGraph = len(relationshipDetailService.getRevenuePercent(root["id"])) > 0 if (relationshipType == "Customers") else False
            group = createNode(str(root["id"]) + "_" + relationshipType, "group", relationshipType, {"classType": "group", "hasGraph": hasGraph})
            root["children"].append(group)
        else:
            group = group[0]

        if len(group["children"]) == GROUP_NODE_LIMIT: continue

        additionalData  = {}
        if item[3] == 1:
            additionalData['isFromRevere'] = item[3]
        if item[4] == 1:
            additionalData['isFromCreditSuisse'] = item[4]

        group["children"].append( createPartyNode(str(itemId), itemType, additionalData) )

def generateJobHistory(itemId):
    jobHistory = []    
    if jobs.has_key(itemId):
        for job in jobs[itemId]:
            jobHistory.append({"title" : "" if job[0] == None else job[0], "company": "" if job[1] == None else job[1], "companyid": "" if job[2] == None else job[2]})
    return jobHistory

def createPartyNode(partyId, type, additionalData):
    partyId = long(partyId)
    partyDetail = parties[partyId]
    name, itemType = partyDetail[1], itemTypeMap[partyDetail[0]]
    sourceid = partyDetail[3] if not itemType == "partygroup" else ""
    
    data = {"classType": itemType, "sourceid" : sourceid, "jobHistory" : generateJobHistory(partyId) }
    if not additionalData == None: data.update(additionalData) # merge in the additional data 
    
    if itemType == "company":
        tickerSymbol, stockExchange, isDNC = partyDetail[4], partyDetail[5], partyDetail[6]
        if not tickerSymbol == 0:
            data["tickerSymbol"] = tickerSymbol
        if not stockExchange == 0:
            data["stockExchange"] = stockExchange
        data["isDNC"] = partyDetail[6]
        data["isPublic"] = (not partyDetail[4] == 0 and not partyDetail[4] == None)

    if itemType == "councilmember":
        data["isDNC"] = partyDetail[4]
        data["isMemberPrograms"] = partyDetail[5]

    if physicalAddresses.has_key(partyId):
        data["continent"] = physicalAddresses[partyId]

    return createNode(partyId, type, name, data);

def createNode(partyId, type, name, data):
    return {
            "id": partyId,
            "type": type,
            "name": name,
            "data": data,
            "children": []
    }

def init():
    start_time = time.time()

    if not os.path.exists(cacheFile_loc):
        os.makedirs(cacheFile_loc)

    logger.info("loading physicaladdresses")
    physicalAddressRows = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"physicaladdress.tmp"), Sql_PhysicalAddress)
    for r in physicalAddressRows:
        physicalAddresses[r[0]] = "" if r[1] == None else r[1]

    logger.info("loading organizations")
    organizations = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"organization.tmp"), Sql_Organizations)
    for r in organizations:
        parties[r[0]] = [r[1], r[2], 0 if r[3] == None else r[3], r[4], 0 if r[5] == None else r[5], 0 if r[6] == None else r[6], r[7]]

    logger.info("loading organizations with council members")
    global orgsWithCMs
    orgsWithCMs = map(lambda x: x[0], dataUtils.loadCachableData(os.path.join(cacheFile_loc,"organizationwithcm.tmp"), Sql_OrganizationsWithCMs))

    logger.info("loading continents")
    continents = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"continents.tmp"), Sql_Continents)
    for r in sorted(continents, key=lambda x: x[0]):
        continentFilters.append(r[0])

    logger.info("loading partygroups")
    partygroups = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"partygroup.tmp"), Sql_PartyGroups)
    for r in partygroups:
        parties[r[0]] = [r[1], r[2], 0 if r[3] == None else r[3], r[4]]

    logger.info("loading people")
    people = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"person.tmp"), Sql_People)
    for r in people:
        parties[r[0]] = [r[1], r[2], 0 if r[3] == None else r[3], r[4], r[5], r[6], r[7]]

    logger.info("loading job records")
    jobRecords = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"jobs.tmp"), Sql_JobRecords)
    for r in jobRecords:
        if not jobs.has_key(r[0]):
            jobs[r[0]] = []
        jobs[r[0]].append([r[1], r[2], r[3]])

    logger.info("loading leads applicants")
    la = dataUtils.loadCachableData(os.path.join(cacheFile_loc,"leadsApplicants.tmp"), Sql_LeadsApplicants)
    for r in la:
        leadsApplicants[r[0]] = [r[1], r[2], r[3]]

    logger.info(str(len(parties)) + " parties loaded in " + str(time.time() - start_time) + " seconds ")


    relationshipDetailService.init(parties)