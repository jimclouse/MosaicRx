import os
import cPickle
import yaml

CACHE_VERSION ="1.1"
cache_loc = "cache"
cache_file = os.path.join(cache_loc,"cacheVersions.tmp")

def isValidCacheFile(fileName, checksum):
	# does the cache file exist?
	if not os.path.exists(cache_file):
		cacheDict = {fileName: checksum}
		resetCache(fileName, cacheDict)
		return False

	# file exists, get the version of the cache
	cacheDict = yaml.load(open(cache_file, "r"))
	if cacheDict.has_key(fileName):
		if cacheDict[fileName] <> checksum:
			cacheDict[fileName] = checksum # reset the checksum version
			resetCache(fileName, cacheDict) # remove file and rewrite config file
			return False
		# no else, if checksum matches, continue on
	else:
		cacheDict[fileName] = checksum # set the checksum version
		resetCache(fileName, cacheDict) # remove file and rewrite config file

	# only positive path - if the cache exists, is good, and the file we want exists
	if os.path.exists(fileName):
		return True

	# catch all - if file doesnt exist, we'll hit this
	return False

def resetCache(fileName, cacheDict):
	# delete cache file if exists
	if os.path.exists(os.path.abspath(fileName)):
		os.remove(os.path.abspath(fileName))
	# write version, then continue
	f = open(cache_file,'w')
	f.write(yaml.dump(cacheDict))


def checksum(st):
	if len(st) == 0: return ""
	return reduce(lambda x,y:x+y, map(ord,st))

companyStopWords = yaml.load(open("./webservice/companyStopWords.yaml",'r'))
abbrvToRemove = companyStopWords.get('stop-words')

def normalizeName(str):
	puncToCollapse = ('.')
	puncToRemove = (',','(',')','-')
	for x in puncToCollapse: str = str.replace(x,'')
	for x in puncToRemove: str = str.replace(x,' ')
	str = str.lower().strip()
	abbrvDict= dict((x, '') for x in abbrvToRemove)
	str = " ".join([abbrvDict[x] if abbrvDict.has_key(x) else x for x in str.split(" ")]) # replace synonyms
	return " ".join(str.split()) # removes any multiples of white space in middle of strings
