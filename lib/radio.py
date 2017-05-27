import sys, getopt, subprocess, re, pickle, time, os

from lib import ffprobe, system, cache

PATH_TO_MUSIC_DB_FILES = '/Users/adamp/Music/MPD/'
PATH_TO_PLAYLIST_FILES = '/Users/adamp/.mpd/playlists/'

def launchPlaylist(listName):
    currentSystemTimeMs = system.getCurrentSystemTimeMs()
    launchPlaylistAtTime(listName, currentSystemTimeMs)

def launchPlaylistAtTime(listName, currentSystemTimeMs):
    print 'listName is', listName
    print 'time is', currentSystemTimeMs

    playlist = getPlaylist(listName)

    startPlaylistAtTime(listName, playlist, currentSystemTimeMs)

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

# Get the number of seconds we are in the current playthrough (aliased time)
# Step through the songs until we find the song we're in the middle of
# Clear out MPC's playlist, load the correct playlist, load the correct song,
#   seek to the correct time, and play
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
        print '========> From Cache'
        return resultList

    resultList = calculatePlaylistDurations(listName)
    cache.writeTo(listName, resultList)

    print '========> Calculated Fresh'
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
