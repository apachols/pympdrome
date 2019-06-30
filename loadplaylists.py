import os
import subprocess
from lib import system
from lib import radio
from time import sleep

ROOT_DIR = '/home/pi'

PLAYLISTDIR = '{}/Music/MPD'.format(ROOT_DIR)

def get_playlists():
    ls = subprocess.check_output(['ls', PLAYLISTDIR], stderr=subprocess.STDOUT)
    return [x for x in ls.split('\n') if x]

# RELOAD ALL PLAYLISTS
for playlist in get_playlists():
    print('Reloading', '||' + playlist + '||', 'shuffle on')
    shuffle = True
    radio.loadPlaylistIntoMPC(playlist, True)
    radio.launchPlaylist(playlist)
    radio.stopPlayback()
    sleep(1)

