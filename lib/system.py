import pickle, os, time, subprocess

from lib import cache

ROOT_DIR = '/home/pi'

MPD_STATE_FILE_NAME = '{}/.mpd/state'.format(ROOT_DIR)
DB_FILE_NAME = '{}/.mpd/database'.format(ROOT_DIR)
TIME_FILE_NAME = '{}/.mpd/hypnotime'.format(ROOT_DIR)
CURRENT_PLAYLIST_FILE_NAME = '{}/.mpd/hypnoplaylist'.format(ROOT_DIR)

#
##
####
# system utils:
#  - getCurrentPlaylistName() returns the name of the current playlist
#  - setCurrentPlaylistName(playlistName) set the system current playlist
#  - getCurrentSystemTimeMs() returns system time in milliseconds
#  - setCurrentSystemTimeMs(newSystemTime) set the system current time
#  - setAliasedSystemTimeMs(newAliasedTimeMs) set the system time so that newAliasedTimeMs is now
#  - reset() starts system time over at zero
####
##
#

# Return the name of the currently playing list, or raise exception
def getCurrentPlaylistName():
    playlistName = readFile(CURRENT_PLAYLIST_FILE_NAME)
    if (playlistName is None):
        raise SystemError("Currently playing playlist not set")
    else:
        return playlistName

# Set the name of the currently playing list
def setCurrentPlaylistName(playlistName):
    writeFile(CURRENT_PLAYLIST_FILE_NAME, playlistName)


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

# Set the current system time to an aliased time (AKA now - targetTime)
def setAliasedSystemTimeMs(newAliasedTimeMs):
    intCurrentTimeMs = int(time.time() * 1000)
    setCurrentSystemTimeMs(intCurrentTimeMs - int(newAliasedTimeMs))

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

# Restart MPD!  After this you will need to re-add files to the system using -l
def restartMpd(killall_mpd=False):
    if killall_mpd:
        subprocess.check_output(['killall', 'mpd'])

    if (os.path.isfile(DB_FILE_NAME)):
        os.remove(DB_FILE_NAME)

    if (os.path.isfile(MPD_STATE_FILE_NAME)):
        os.remove(MPD_STATE_FILE_NAME)

    subprocess.check_output(['mpd'])

# Reset the system to a correct initial state
def reset():  
    subprocess.check_output(['mpc', 'repeat', 'on'])
    subprocess.check_output(['mpc', 'crossfade', '1'])

    if (os.path.isfile(TIME_FILE_NAME)):
        os.remove(TIME_FILE_NAME)

    if (os.path.isfile(CURRENT_PLAYLIST_FILE_NAME)):
        os.remove(CURRENT_PLAYLIST_FILE_NAME)

    cache.clearCache()

# error message
class SystemError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg
