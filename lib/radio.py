import subprocess, time

from lib import ffprobe, system, cache

DEBUG_PRINTS=False

PATH_TO_MUSIC_DB_FILES = '/Users/adamp/Music/MPD/'
PATH_TO_PLAYLIST_FILES = '/Users/adamp/.mpd/playlists/'

def skipToNextSong():
    # Figure out what we are playing currently
    currentSystemTimeMs = system.getCurrentSystemTimeMs()
    currentPlaylistName = system.getCurrentPlaylistName()
    playlistData = getPlaylist(currentPlaylistName)
    # Find the start of the next song, and reset the system time so it plays immediately
    nextSongStartTimeMs = getAliasedTimeForStartOfNextSong(currentPlaylistName, playlistData, currentSystemTimeMs)
    newSystemTimeMs = system.newSystemTimeForAliasedStartTime(nextSongStartTimeMs)
    system.setCurrentSystemTimeMs(newSystemTimeMs)
    # Now that ths system time says the next song is up, launch current playlist
    launchPlaylist(currentPlaylistName)

def launchPlaylist(listName):
    currentSystemTimeMs = system.getCurrentSystemTimeMs()
    launchPlaylistAtTime(listName, currentSystemTimeMs)
    system.setCurrentPlaylistName(listName)

def launchPlaylistAtTime(listName, currentSystemTimeMs):
    if (DEBUG_PRINTS):
        print 'playing playlist named', listName
        print 'playing at time', currentSystemTimeMs

    playlist = getPlaylist(listName)
    startPlaylistAtTime(listName, playlist, currentSystemTimeMs)
    system.setCurrentPlaylistName(listName)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Start a playlist at a given time.  If given time is after end of playlist,
# loop around to the start.
#
# For example:
# - If playlist is 99000 ms, and time is 41000, playlist starts at 41000ms
# - If playlist is 99000 ms, and time is 150200, playlist starts at 51200ms (wrapped once)
# - If playlist is 99000 ms, and time is 250300, playlist starts at 52300ms (wrapped twice)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

# Start the requested playlist at the target time
def startPlaylistAtTime(listName, playlistData, targetPlaylistTimeMs):
    indexAndSeekTime = getPlaylistIndexAndSeekTime(listName, playlistData, targetPlaylistTimeMs)
    playlistDataIndex = indexAndSeekTime[0]
    seekTime = indexAndSeekTime[1]
    playAtIndexWithSeekTime(listName, playlistDataIndex + 1, seekTime)

# Clear out MPC's playlist, load the correct playlist, load the correct song,
#   seek to the correct time, and play
def playAtIndexWithSeekTime(listName, index, seekTime):
    subprocess.check_output(['mpc', 'clear'])
    subprocess.check_output(['mpc', 'load', listName])
    subprocess.check_output(['mpc', 'play', str(index)])
    subprocess.check_output(['mpc', 'pause'])
    subprocess.check_output(['mpc', 'seek', seekTime])
    subprocess.check_output(['mpc', 'play'])

# Get the number of seconds we are in the current playthrough (aliased time)
# Step through the songs until we find the song we're in the middle of
# Return the zero-offset index of that song and the number of milliseconds we are through it
def getPlaylistIndexAndSeekTime(listName, playlistData, targetPlaylistTimeMs):
    aliasedTimeMs = getAliasedTimeForPlaylistData(playlistData, targetPlaylistTimeMs)

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

    return (playlistDataIndex, getSeekTimeString(seekTime))

# Loop through playlist data, return aliased start time of next song
def getAliasedTimeForStartOfNextSong(listName, playlistData, currentSystemTimeMs):
    aliasedTimeMs = getAliasedTimeForPlaylistData(playlistData, currentSystemTimeMs)
    playlistDataIndex = 0
    startOfNextSongMarker = 0
    for playlistDataIndex, song in enumerate(playlistData):
        playlistDataIndex += 1
        currentSongLength = song[1]
        startOfNextSongMarker += currentSongLength
        # if the start of next song is after the aliased time, stop searching, we found it
        if (aliasedTimeMs < startOfNextSongMarker):
            break
    return startOfNextSongMarker

def printPlaylistSeekSanityCheck(idx, songLength, seekTime, endOfSong):
    if (DEBUG_PRINTS):
        print '('+str(idx)+')', 'songLength', songLength, 'seekTime', seekTime, 'endOfSong', endOfSong

def getSeekTimeString(seekTimeInMs):
    seekTimeRoundedSeconds = int(seekTimeInMs/1000)
    return '+00:00:' + str(seekTimeRoundedSeconds)

def getAliasedTimeForPlaylistData(playlistData, targetPlaylistTimeMs):
    totalPlaylistTimeMs = sum( int(duration) for filename,duration in playlistData )
    return getAliasedTime(targetPlaylistTimeMs, totalPlaylistTimeMs)

def getAliasedTime(targetPlaylistTimeMs, playlistLengthMs):
    aliasedTime = int(targetPlaylistTimeMs) % int(playlistLengthMs)
    return aliasedTime

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Calculate durations of songs in playlist and cache them on disk
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#

# Look in the cache for playlist durations
# If not in cache, calculate playlist durations and write cache
# Return durations for songs in playlist as array
def getPlaylist(listName):
    resultList = cache.readFrom(listName)

    if not resultList is None:
        return resultList

    if (DEBUG_PRINTS):
        print '========> Recalculating playlist durations using ffprobe, please wait...'
    t1 = time.time()
    resultList = calculatePlaylistDurations(listName)
    cache.writeTo(listName, resultList)
    t2 = time.time()
    if (DEBUG_PRINTS):
        print '========> Playlist recalculations complete (in', t2-t1, 'seconds)'

    return resultList

# Use ffprobe to calculate playlist durations
# Return playlist durations as array
def calculatePlaylistDurations(listName):
    files = getFilesInPlaylist(listName)

    result = []

    for aFile in files:
        fileUri = PATH_TO_MUSIC_DB_FILES + aFile
        try:
            duration = ffprobe.getFileDurationUsingFFProbe(fileUri)
            row = (fileUri, duration)
            result.append(row)
        except Exception as e:
            print 'Error in', fileUri,
            print '------->', ''.join(e.msg)

    return result

# Read an m3u file from the MPC playlist directory
# Return all the files in the m3u playlist file as array
def getFilesInPlaylist(listName):
    with open(PATH_TO_PLAYLIST_FILES + listName + '.m3u') as f:
        content = f.readlines()

    return [line.strip() for line in content]
