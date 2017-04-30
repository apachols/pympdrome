import sys, getopt, subprocess, re, pickle, time, os

TIME_FILE_NAME = '/Users/adamp/.mpd/hypnotime'
PATH_TO_MUSIC_DB_FILES = '/Users/adamp/Music/MPD/'
CACHE_FILE_PATH = '/Users/adamp/.mpd/hypnocache/'
PATH_TO_PLAYLIST_FILES = '/Users/adamp/.mpd/playlists/'

#
#  Brew install mpd
#  Brew install ffmpeg
#  Brew install mpc
#
#  Restart MPD
#      killall mpd
#      rm ~/.mpd/database && touch ~/.mpd/database
#      rm ~/.mpd/state
#      mpd
#
#  python launch.py -r # SYSTEM RESTART
#
#  Clear playlist cache
#      rm ~/.mpd/hypnocache/*
#
#  Re-add playlist
#      mpc clear
#      mpc add folder01
#      mpc save playlist01
#      mpc clear
#      mpc add folder02
#      mpc save playlist02
#      mpc clear
#      mpc add folder03
#      mpc save playlist03
#
#  python launch.py -p playlist01
#
#      mpc crossfade 1
#      while true; do python launch.py -p playlist01; sleep 8; done
#      sleep 4; while true; do python launch.py -p playlist02; sleep 8; done
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  TODO:
#    * When using -t <time> to start the system, write the system time file again
#    * Configs instead of hardcoded paths and such
#    * Verbose mode
#    * Split into a couple of different files
#    * Build a way for infinitton buttons to launch the playlists
#    * Build controls for other button functions (volume? stop? skip ahead?)
#    * Make sure to turn on playlist repeat for mpc (`mpc repeat on`?)
#    * Fix the way you reload playlists after changing the folders, too many steps
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#

def launchPlaylist(listName):
    currentPlaylistTimeMs = getCurrentPlaylistTimeMs()
    launchPlaylistAtTime(listName, currentPlaylistTimeMs)

def launchPlaylistAtTime(listName, currentPlaylistTimeMs):
    print 'listName is', listName
    print 'time is', currentPlaylistTimeMs

    playlist = getPlaylist(listName)

    startPlaylistAtTime(listName, playlist, currentPlaylistTimeMs)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

def getCurrentPlaylistTimeMs():
    systemStartTimeMs = readTimeFile()

    # time() returns a floating point number in whole seconds since the epoch
    intCurrentTimeMs = int(time.time() * 1000)

    if (systemStartTimeMs is None):
        writeTimeFile(intCurrentTimeMs)
        return 0
    else:
        return intCurrentTimeMs - systemStartTimeMs

def readTimeFile():
    try:
        with open(TIME_FILE_NAME, 'rb') as filehandle:
            return pickle.load(filehandle)
    except Exception as e:
        return None

def writeTimeFile(currentTimeMs):
    with open(TIME_FILE_NAME, 'wb') as filehandle:
        pickle.dump(currentTimeMs, filehandle)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

def startPlaylistAtTime(listName, playlistData, currentTimeMs):
    totalPlaylistTimeMs = sum( int(duration) for filename,duration in playlistData )
    print 'total duration in ms:', totalPlaylistTimeMs

    aliasedTimeMs = getAliasedTime(currentTimeMs, totalPlaylistTimeMs)
    print 'aliased time', aliasedTimeMs

    endOfPreviousSongMarker = 0
    for playlistDataIndex, song in enumerate(playlistData):
        # seek time is how far we have to go from the end of the previous song to the target time
        seekTime = aliasedTimeMs - endOfPreviousSongMarker

        # pull the current song length and advance the end-of-song marker by one song
        currentSongLength = song[1]
        endOfPreviousSongMarker += currentSongLength

        # debug print a sanity check for this loop
        printPlaylistSeekSanityCheck(playlistDataIndex, currentSongLength, seekTime, endOfPreviousSongMarker)

        # if we need to seek to a time in the middle of this song, we've found our song, quit looking.
        if (seekTime < currentSongLength):
            break

    # MPC Playlists are indexed from 1, somewhat reasonably.
    playAtIndexWithSeekTime(listName, playlistDataIndex + 1, getSeekTimeString(seekTime))

def printPlaylistSeekSanityCheck(idx, songLength, seekTime, endOfSong):
    print '('+str(idx)+')', 'songLength', songLength, 'seekTime', seekTime, 'endOfSong', endOfSong

def getSeekTimeString(seekTimeInMs):
    seekTimeRoundedSeconds = int(seekTimeInMs/1000)
    return '+00:00:' + str(seekTimeRoundedSeconds)

def playAtIndexWithSeekTime(listName, index, seekTime):
    subprocess.check_output(['mpc', 'clear'])
    subprocess.check_output(['mpc', 'load', listName])
    subprocess.check_output(['mpc', 'play', str(index)])
    subprocess.check_output(['mpc', 'pause'])
    subprocess.check_output(['mpc', 'seek', seekTime])
    subprocess.check_output(['mpc', 'play'])

def getAliasedTime(currentTimeMs, playlistLengthMs):
    aliasedTime = int(currentTimeMs) % int(playlistLengthMs)
    return aliasedTime

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

def getPlaylist(listName):
    resultList = readFromCache(listName)

    if not resultList is None:
        print '========> From Cache'
        return resultList

    resultList = calculatePlaylistDurations(listName)
    writeToCache(listName, resultList)

    print '========> Calculated Fresh'
    return resultList

def cacheFileName(listName):
    return CACHE_FILE_PATH + listName

def readFromCache(listName):
    try:
        with open(cacheFileName(listName), 'rb') as filehandle:
            return pickle.load(filehandle)
    except Exception as e:
        return None

def writeToCache(listName, resultList):
    with open(cacheFileName(listName), 'wb') as filehandle:
        pickle.dump(resultList, filehandle)

def calculatePlaylistDurations(listName):
    files = getFilesInPlaylist(listName)

    result = []

    for aFile in files:
        fileUri = PATH_TO_MUSIC_DB_FILES + aFile
        try:
            duration = getFileDurationUsingFFProbe(fileUri)
            row = (fileUri, duration)
            result.append(row)
        except Exception as e:
            print 'Error in', fileUri,
            print '------->', ''.join(e.msg)

    return result

def getFilesInPlaylist(listName):
    # mpc does not print a nice list of file paths for a playlist.
    # the playlist file, however, is exactly that.

    with open(PATH_TO_PLAYLIST_FILES + listName + '.m3u') as f:
        content = f.readlines()

    return [line.strip() for line in content]

def getFileDurationUsingFFProbe(fileUri):
    ffprobeOutput = subprocess.check_output(['ffprobe', fileUri], stderr=subprocess.STDOUT)
    return durationFromFFProbeResult(ffprobeOutput)

def durationFromFFProbeResult(ffprobeResult):
    ffprobeOutputLines = ffprobeResult.split('\n')
    for aLine in ffprobeOutputLines:
        aLineStripped = aLine.strip()
        if aLineStripped.startswith('Duration'):
            totalMilliseconds = durationFromFFProbeDurationLine(aLineStripped)
            return totalMilliseconds
    raise FFProbeError("No duration found in FFProbe result")

def durationFromFFProbeDurationLine(line):
    matches = re.match(r"Duration: (\d\d):(\d\d):(\d+\.\d+)", line)
    if matches:
        hours, minutes, seconds = matches.groups(0)
        totalSeconds = int(hours) * 60 * 60 + int(minutes) * 60 + float(seconds)
        totalMilliseconds = int(totalSeconds*1000)
        return totalMilliseconds
    raise FFProbeError("Bad format for FFProbe duration line=" + line)

class FFProbeError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# TODO, there's a lot we can do here to help the system reboot gracefully:
#       - clear 'hypnocache' files
#
def systemReset():
    os.remove(TIME_FILE_NAME)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
def main(argv):
    help = """
        # switch to <playlist>
        launch.py -p <playlist>
        OR
        # switch to <playlist> at the specified time
        launch.py -p <playlist> -t <time>
        OR
        # reset the system
        launch.py -r
    """
    playlist = ''
    time = ''
    try:
        opts, args = getopt.getopt(argv,"hrp:t:",["playlist=","time="])
    except getopt.GetoptError:
        print help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help
            sys.exit()
        elif opt in ("-r"): #, "--reset"):
            print 'SYSTEM RESET'
            systemReset()
            exit()
        elif opt in ("-p"): #, "--playlist"):
            playlist = arg
        elif opt in ("-t"): #, "--time"):
            time = arg

    if (time == ''):
        launchPlaylist(playlist)
    else:
        launchPlaylistAtTime(playlist, time)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
if __name__ == "__main__":
    main(sys.argv[1:])