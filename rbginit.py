import os
import subprocess
from lib import system
from lib import radio
from time import sleep

ROOT_DIR = '/Users/adamp'
# ROOT_DIR = '/home'

PLAYLISTDIR = '{}/Music/MPD'.format(ROOT_DIR)
MPD_STATE_FILE_NAME = '{}/.mpd/state'.format(ROOT_DIR)
DB_FILE_NAME = '{}/.mpd/database'.format(ROOT_DIR)

def get_playlists():
    ls = subprocess.check_output(['ls', PLAYLISTDIR], stderr=subprocess.STDOUT)
    return [x for x in ls.split('\n') if x]

#
# # CONTAINER INIT # #
#

# START MPD

# if (os.path.isfile(MPD_STATE_FILE_NAME)):
#     os.remove(MPD_STATE_FILE_NAME)

# if (os.path.isfile(DB_FILE_NAME)):
#     os.remove(DB_FILE_NAME)

# subprocess.check_output(['mpd'])

# sleep(3)
# print 'sleeping...'

# CLEAR HYPNO CACHE FILES
# system.reset()

# RELOAD ALL PLAYLISTS
for playlist in get_playlists():
    print 'Reloading', '||' + playlist + '||', 'shuffle on'
    shuffle = True
    radio.loadPlaylistIntoMPC(playlist, True)
    radio.launchPlaylist(playlist)
    radio.stopPlayback()
    sleep(1)

