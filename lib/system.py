import pickle, os, time

TIME_FILE_NAME = '/Users/adamp/.mpd/hypnotime'
PLAYLIST_FILE_NAME = '/Users/adamp/.mpd/hypnoplaylist'

#
##
####
# system utils:
#  - getCurrentSystemTimeMs() returns system time in milliseconds
#  - reset() starts system time over at zero
####
##
#

# Return the name of the currently playing list, or raise exception
def getCurrentPlaylistName():
    playlistName = readFile(PLAYLIST_FILE_NAME)
    if (playlistName is None):
        raise SystemError("Currently playing playlist not set")
    else:
        return playlistName

# Set the name of the currently playing list
def setCurrentPlaylistName(playlistName):
    writeFile(PLAYLIST_FILE_NAME, playlistName)

def newSystemTimeForAliasedStartTime(aliasedStartTimeMs):
    intCurrentTimeMs = int(time.time() * 1000)
    return  intCurrentTimeMs - aliasedStartTimeMs

# Return the current system time in ms, AKA time since system start
def getCurrentSystemTimeMs():
    systemStartTimeMs = readFile(TIME_FILE_NAME)

    # time() returns a floating point number in whole seconds since the epoch
    intCurrentTimeMs = int(time.time() * 1000)

    if (systemStartTimeMs is None):
        writeFile(TIME_FILE_NAME, intCurrentTimeMs)
        return 0
    else:
        return intCurrentTimeMs - systemStartTimeMs

# Set the name of the currently playing list
def setCurrentSystemTimeMs(newSystemTime):
    writeFile(TIME_FILE_NAME, newSystemTime)

# Read a file from disk that we wrote before (formatted for pickle)
def readFile(filename):
    try:
        with open(filename, 'rb') as filehandle:
            return pickle.load(filehandle)
    except Exception as e:
        return None

# Write a python to disk (formatted for pickle)
def writeFile(filename, data):
    with open(filename, 'wb') as filehandle:
        pickle.dump(data, filehandle)

#
# TODO MORE STUFF HERE
#
def reset():
    os.remove(TIME_FILE_NAME)

# error message
class SystemError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg