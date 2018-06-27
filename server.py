
from flask import Flask
from flask import render_template
from flask import redirect

from lib import radio, system

import subprocess

app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

def get_playlists():
    ls = subprocess.check_output(['ls', '/Users/adamp/Music/MPD'], stderr=subprocess.STDOUT)
    return [x for x in ls.split('\n') if x]

playlists = get_playlists()

@app.route("/")
def index(playing=""):
    return render_template(
        "index.html",
        playlists=playlists,
        playing=playing
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

