import sys, getopt
from flask import Flask
from flask import render_template
from flask import redirect

from lib import radio, system

import subprocess

silent_disco = False

app = Flask(__name__)

ROOT_DIR = '/Users/adamp'
ROOT_DIR = '/home'

PLAYLISTDIR = '{}/Music/MPD'.format(ROOT_DIR)
COLOR = '/etc/color.txt'

def file_get_contents(filename):
    with open(filename) as f:
        return f.read()

color = file_get_contents(COLOR)

def get_playlists():
    ls = subprocess.check_output(['ls', PLAYLISTDIR], stderr=subprocess.STDOUT)
    playlists = [x for x in ls.split('\n') if x]
    if silent_disco:
        return [
            x for x in playlists
            if 'step' in x or 'dance' in x or 'groove' in x or 'medium' in x
        ]
    print(silent_disco)
    return playlists

@app.route("/")
def index(playing=""):
    return render_template(
        "index.html",
        playlists=get_playlists(),
        playing=playing,
        color=color
    )

@app.route("/next/")
@app.route("/next/<playlist>")
def next(playlist=None):
    if not playlist:
        playlist = system.getCurrentPlaylistName()
    radio.skipToNextSong()
    return launch(playlist)

@app.route("/stop/")
@app.route("/stop/<playlist>")
def stop(playlist=""):
    radio.stopPlayback()
    return index("")

@app.route("/playlist/<playlist>")
def launch(playlist):
    radio.launchPlaylist(playlist)
    return index(playlist)

if __name__ == '__main__':
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "d", ["disco="])
    if len(args) and args[0] == 'disco':
        silent_disco = True
    app.run(debug=True, host='0.0.0.0')