
from flask import Flask
from flask import render_template
from flask import redirect

from lib import radio, system

import subprocess

app = Flask(__name__)

def get_playlists():
    ls = subprocess.check_output(['ls', '/Users/adamp/Music/MPD'], stderr=subprocess.STDOUT)
    return [x for x in ls.split('\n') if x]

playlists = get_playlists()

@app.route("/")
def index():
    return render_template('index.html', playlists=playlists)

@app.route("/next")
def next():
    radio.skipToNextSong()
    return redirect('/')

@app.route("/stop")
def stop():
    radio.stopPlayback()
    return redirect('/')

@app.route('/playlist/<playlist>')
def playlist(playlist):
    radio.smartHandleButtonPress(playlist)
    return redirect('/')

