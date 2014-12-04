#! python
#! coding: utf-8
# Runs queries against SQL Server database
import logging
import MySQLdb
import time
import utils
import ConfigParser
import os
import cPickle

#initialize logger
logger = logging.getLogger('Mosaic.dataUtil')
    
# MySQL Data utils
def getMysqlConnection():
	config = ConfigParser.RawConfigParser()
	config.read(os.path.join(os.path.dirname(__file__),'../../configs/mosaic_web.cfg'))

	host = config.get('Database', 'host')
	user = config.get('Database', 'user')
	pwd = config.get('Database', 'pwd')
	db = config.get('Database', 'db')
	sock = config.get('Database', 'sock')

	try:
		if sock == "": return MySQLdb.connect(host=str(host),user=str(user),passwd=str(pwd),db=str(db))
		else:         return MySQLdb.connect(unix_socket=str(sock),host=str(host),user=str(user),passwd=str(pwd),db=str(db))
	except Exception as e:
		logger.error(e)
		raise


# loadData will check to see if the needed data is in file cache and still valid and return that file
# or will go out to the database to fetch the data and write it to cache if necessary
def loadCachableData(fileName, sql):
	if utils.isValidCacheFile(fileName, utils.checksum(sql)):
		return cPickle.load(open(fileName, "rb"))
	else:
		try:
			conn = getMysqlConnection()
			cur = conn.cursor()
			cur.execute(sql)
			rows = cur.fetchall()
			cur.close()
		except Exception as e:
			logger.error("query failed: " + sql + "\n" + str(e))
			raise

		if not rows == None and len(rows) > 0:
			cPickle.dump(rows, open(fileName, "wb"), True)
			return rows
		else:
			logger.error("SQL ERROR: Query Returned 0 Results: " + fileName)
			raise

def fetchAll(sql):
	try:
		conn = getMysqlConnection()
		cur = conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		cur.close()
		return rows
	except Exception as e:
		logger.error("query failed: " + sql + "\n" + str(e))
		raise
		