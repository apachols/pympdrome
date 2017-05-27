import sys, getopt

from lib import radio, system

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

def main(argv):
    help = """
        # switch to <playlist>
        launch.py -p <playlist>
        OR
        # switch to <playlist> at the specified time
        launch.py -p <playlist> -t <time>
        OR
        # skip to next song
        launch.py -n
        OR
        # reset the system
        launch.py -r
    """
    playlist = ''
    time = ''
    try:
        opts, args = getopt.getopt(argv,"hrnp:t:",["playlist=","time="])
    except getopt.GetoptError:
        print help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help
            sys.exit()
        elif opt in ("-n"): #, "--next"):
            print 'Next!'
            radio.skipToNextSong()
            exit()
        elif opt in ("-r"): #, "--reset"):
            print 'SYSTEM RESET'
            system.reset()
            exit()
        elif opt in ("-p"): #, "--playlist"):
            playlist = arg
        elif opt in ("-t"): #, "--time"):
            time = arg

    if (playlist == ''):
        print 'Input Error: no playlist specified'
        exit(1)

    if (time == ''):
        radio.launchPlaylist(playlist)
    else:
        radio.launchPlaylistAtTime(playlist, time)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
if __name__ == "__main__":
    main(sys.argv[1:])