import pickle, os

CACHE_FILE_PATH = '/Users/adamp/.mpd/hypnocache/'

#
##
####
# uses pickle to cache information on disk
####
##
#

def cacheFileName(listName):
    return CACHE_FILE_PATH + listName

def readFrom(listName):
    try:
        with open(cacheFileName(listName), 'rb') as filehandle:
            return pickle.load(filehandle)
    except Exception as e:
        return None

def writeTo(listName, resultList):
    with open(cacheFileName(listName), 'wb') as filehandle:
        pickle.dump(resultList, filehandle)

def clearCacheFile(listName):
    os.remove(cacheFileName(listName))

def clearCache():
    (dirpath, dirnames, filenames) = os.walk(CACHE_FILE_PATH).next()
    for filename in filenames:
        clearCacheFile(filename)