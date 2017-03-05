import sys, getopt, subprocess, re, pickle

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
#  Clear playlist cache
#      rm ~/.mpd/hypnocache/*
#
#  Re-add playlist
#      mpc clear
#      mpc add folder01
#      mpc clear
#      mpc add folder02
#
#  python launch.py -p folder01 -t 0
#
#  Oh no...
#      mpc crossfade 1
#      TIME=90000; while true; do TIME=$(($TIME+5000)) && python launch.py -p folder01 -t $TIME; sleep 5; done
#      TIME=0; while true; do TIME=$(($TIME+5000)) && python launch.py -p folder02 -t $TIME; sleep 5; done
#
#  Oh yes.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
#  TODO:
#    * Build global time tracker (timer.py) that calls launch.py
#    * Build a way for infinitton buttons to communicate with global time tracker (timer.py)
#    * Fix the way you reload playlists after changing the folders, too many steps
#    * Build controls for other button functions (volume? stop? system restart? skip ahead?)
#    * Make sure to turn on playlist repeat for mpc (`mpc repeat on`?)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

def launch(listName, currentTimeMs):
    print 'listName is', listName
    print 'time is', currentTimeMs

    playlist = getPlaylist(listName)

    startPlaylistAtTime(playlist, currentTimeMs)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

def startPlaylistAtTime(playlist, currentTimeMs):
    for song in playlist:
        print song

    totalPlaylistTimeMs = sum( int(duration) for filename,duration in playlist )
    print 'total duration in ms:', totalPlaylistTimeMs

    aliasedTimeMs = getAliasedTime(currentTimeMs, totalPlaylistTimeMs)
    print 'aliased time', aliasedTimeMs

    # If we are in the first song, just go there
    seekTimeMs =  aliasedTimeMs

    # Look at the end of the first song (INDEX ZERO, HERE) to see if we need to skip ahead
    songEndTimeMs = playlist[0][1]

    # MPC Playlists are indexed from 1, somewhat reasonably.  If we are in the first song, return 1
    playlistIndex = 1

    print 'index', playlistIndex, 'songEndTimeMs', songEndTimeMs, 'seekTimeMs', seekTimeMs

    # Keep going until we find an end time that is PAST the aliased time.
    while songEndTimeMs <= aliasedTimeMs:

        # If this is our last loop, the seek time in target song is target time - end of last song
        seekTimeMs = aliasedTimeMs - songEndTimeMs

        # move us forward 1 song; for last loop, songEndTime will be after aliasedTime
        songEndTimeMs += playlist[playlistIndex][1]

        # move us forward one song
        playlistIndex += 1

        print 'index', playlistIndex, 'songEndTimeMs', songEndTimeMs, 'seekTimeMs', seekTimeMs

    print "playlist index", playlistIndex

    seekTimeString = getSeekTimeString(seekTimeMs)

    playAtIndexWithSeekTime(playlistIndex, seekTimeString)

def getSeekTimeString(seekTimeInMs):
    seekTimeRoundedSeconds = int(seekTimeInMs/1000)
    # print "seek time in seconds", seekTimeRoundedSeconds
    return '+00:00:' + str(seekTimeRoundedSeconds)

def playAtIndexWithSeekTime(index, seekTime):
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
# For later:  we need to be able to invalidate this cache :|
# Maybe we can have a restart command that wipes them all?
# But we need a python daemon or something that will keep track of the time...
# or to store the start time in a file
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
    return '/Users/adamp/.mpd/hypnocache/' + listName

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
    pathToFiles = '/Users/adamp/Music/MPD/'

    files = getFilesInPlaylist(listName)

    result = []

    for aFile in files:
        fileUri = pathToFiles + aFile
        try:
            duration = getFileDurationUsingFFProbe(fileUri)
            row = (fileUri, duration)
            result.append(row)
        except Exception as e:
            print 'Error in', fileUri,
            print '------->', ''.join(e.msg)

    return result

def getFilesInPlaylist(listName):
    commandOutput = subprocess.check_output(['mpc', 'ls', listName])
    return commandOutput.strip().split('\n')

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
def main(argv):
    help = 'launch.py -p <playlist> -t <time>'
    playlist = ''
    time = ''
    try:
        opts, args = getopt.getopt(argv,"hp:t:",["playlist=","time="])
    except getopt.GetoptError:
        print help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help
            sys.exit()
        elif opt in ("-p"): #, "--playlist"):
            playlist = arg
        elif opt in ("-t"): #, "--time"):
            time = arg

    launch(playlist, time)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
if __name__ == "__main__":
    main(sys.argv[1:])