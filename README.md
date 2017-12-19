# pympdrome

###### mpd driver for radio hypnodrome

pympdrome uses the MPD headless music player to simulate gapless playback and station switching between any number of locally stored mp3 playlists.

For example, say you have a 'Slow Jams' playlist, and a 'Hard Rock' playlist.  If the Hard Rock playlist is in the middle of a KYUSS song (e.g. at 3:40), and you switch to the Slow Jams playlist, you'll start in the middle of whatever song is playing on the Slow Jams "station" (e.g. Alicia Keys).  Switch back to Hard Rock after 5 seconds, and you'll be right where you left off - at 3:45!

###### software you will need to install:

MPD:  Music Player Daemon, a headless music player for *nix / osx / etc

MPC: 'A minimalist command line interface to MPD.'

ffmpeg:  '...record, convert and stream audio and video.'

Python 2.7 is required to run the radio launcher.

## Installation instructions for OS X

#### Install the basics: MPD, FFMPEG, MPC

1. Get homebrew
	* https://brew.sh/
2. brew install mpd
	* https://www.musicpd.org/
3. brew install ffmpeg
	* https://ffmpeg.org/
4. brew install mpc
	* https://www.musicpd.org/clients/mpc/

#### Get MPD working on OSX

I used these instructions and they worked flawlessly:

http://mpd.wikia.com/wiki/Mpd_on_OS_X_Snow_Leopard

Reproducing here:

1. Create a file called ~/.mpdconf and add the following:
```
music_directory         "~/Music/MPD"
playlist_directory              "~/.mpd/playlists"
db_file                 "~/.mpd/database"
pid_file                        "~/.mpd/pid"
state_file              "~/.mpd/state"
sticker_file                    "~/.mpd/sticker.sql"
port                            "6600"
auto_update     "yes"
audio_output {
        type            "osx"
        name            "My Mac Device"
        mixer_type      "software"
}
```

2. Create the ~./mpd directory, playlists dir, and database file
```
mkdir ~/.mpd
mkdir ~/.mpd/playlists
touch ~/.mpd/database
```

4. Simply type 'mpd' at the command line

```
$ mpd
exception: bind to '0.0.0.0:6600' failed (continuing anyway, because binding to '[::]:6600' succeeded): Failed to bind socket: Address already in use
```

(^ I get this cool error evey time.  doesn't seem to matter!)

You may also see an error that says "database corrupted"... that's likely due to our creation of an empty database file in ./mpd in Step 2 above.

#### Get MPC working on OSX

This was a lot of trial and error for me; MPC seems to have approximately zero documentation outside of its command line help print :+1:

Here are the MPC commands that are interesting for this project (to see all options type 'mpc help')

```
  mpc                               Display status
  mpc help                          Display the command list
  mpc add <uri>                     Add a song to the current playlist
  mpc current                       Show the currently playing song
  mpc del <position>                Remove a song from the current playlist
  mpc play [<position>]             Start playing at <position>
  mpc next                          Play the next song in the current playlist
  mpc prev                          Play the previous song in the current playlist
  mpc pause                         Pauses the currently playing song
  mpc pause-if-playing              Pause, but exits with failure if not playing
  mpc toggle                        Toggles Play/Pause, plays if stopped
  mpc cdprev                        Compact disk player-like previous command
  mpc stop                          Stop the currently playing playlists
  mpc seek [+-][HH:MM:SS]|<0-100>%  Seeks to the specified position
  mpc clear                         Clear the current playlist
  mpc shuffle                       Shuffle the current playlist
  mpc playlist [<playlist>]         Print <playlist>
  mpc listall [<file>]              List all songs in the music dir
  mpc ls [<directory>]              List the contents of <directory>
  mpc lsplaylists                   List currently available playlists
  mpc load <file>                   Load <file> as a playlist
  mpc save <file>                   Save a playlist as <file>
  mpc volume [+-]<num>              Set volume to <num> or adjusts by [+-]<num>
  mpc crossfade [<seconds>]         Set and display crossfade settings
```

Anyway, next, we'll add some music to the directory we specified as "music_directory" in the mpd config up above:

```
cp ~/Music/MP3/SteelyDan/Aja/* ~/Music/MPD/folder01
cp ~/Music/MP3/FleetFoxes/FleetFoxes ~/Music/MPD/folder02
```
Each folder created here is essentially a playlist.

Add each playlist to MPC:
```
mpc add folder01
mpc save playlist01
mpc clear
mpc add folder02
mpc save playlist02
mpc clear
```

Start playback (you should hear musical noises when you do this):
```
mpc load playlist01
mpc play
```

Jane, get me off this crazy thing!
```
mpc stop
```

#### Set up pympdrome

Create one more directory that we'll need to run pympdrome (this is where cached information about all the tracks in the playlist is stored).

```
mkdir ~/.mpd/hypnocache/
```

#### Get pympdrome command help
```
 $ python launch.py -h

        # switch to <playlist>
        launch.py -p <playlist>
        OR
        # switch to <playlist> at the specified time
        launch.py -p <playlist> -t <time>
        OR
        # reset the system
        launch.py -r
```

#### Start a playlist at the system time with pympdrome

```
 $ python launch.py -p <playlist>
```
The 'playlist' arg will be one of the folders you added; it will play at the global elapsed time since system start.

#### Start a playlist at a time with pympdrome

```
 $ python launch.py -p <playlist> -t <time>
```

The 'playlist' arg will be one of the folders you added; 'time' will be playlist offset time in milliseconds.

```
# Play Steely Dan at the global time:
python launch.py -p playlist01
```

```
# Play Fleet Foxes starting at 90 seconds:
python launch.py -p playlist02 -t 90000
```

```
# Turn on cross fade, and then keep switching between the two playlists:
mpc crossfade 1
# In one terminal window:
while true; do python launch.py -p playlist01; sleep 8; done
# In another terminal window:
sleep 4; while true; do python launch.py -p playlist02; sleep 8; done
```

![Magic!](https://media.giphy.com/media/12NUbkX6p4xOO4/giphy.gif)

#### How to restart MPD (e.g. if it starts crashing...)

```
killall mpd
rm ~/.mpd/database && touch ~/.mpd/database
rm ~/.mpd/state
mpd
```

#### System restart for pympdrome
```
 $ python launch.py -r
```

#### Refresh the system after changing the files in the playlists
```
killall mpd
rm ~/.mpd/database && touch ~/.mpd/database
rm ~/.mpd/state
mpd

# Clear playlist cache
rm ~/.mpd/hypnocache/*

# Clear out current queue
mpc clear

# Remove playlists
mpc rm playlist01
mpc rm playlist02

# Add folders back in and save to playlists
mpc add folder01
mpc save playlist01
mpc clear
mpc add folder02
mpc save playlist02
mpc clear
```
