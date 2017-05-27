import sys, getopt

from lib import radio, system

#
##
####
# Radio Hypnodrome CLI - see help print below for available commands
####
##
#

def main(argv):
    help = """
        launch.py -s <playlist>             switch to playlist OR next song if playing already

        launch.py -p <playlist>             switch to <playlist>

        launch.py -p <playlist> -t <time>   switch to <playlist> at the specified time

        launch.py -l -p <playlist>          reload <playlist> into MPD after file changes

        launch.py -n                        skip to next song

        launch.py -r                        reset the system

        launch.py -h                        display this help text
    """
    playlist = ''
    time = ''
    smart = False
    load = False
    try:
        opts, args = getopt.getopt(argv,"hrnls:p:t:",["playlist=","playlist=","time="])
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
            system.restartMpd()
            system.reset()
            exit()
        elif opt in ("-l"): #, "--load"):
            load = True
        elif opt in ("-s"): #, "--smart"):
            smart = True
            playlist = arg
        elif opt in ("-p"): #, "--playlist"):
            playlist = arg
        elif opt in ("-t"): #, "--time"):
            time = arg

    # Check input; playlist name is not optional for the below commands
    if (playlist == ''):
        print '========ATTENTION PLEASE=========='
        print 'Input Error: no playlist specified'
        print '=================================='
        print help
        exit(1)

    if (load):
        print 'Reloading', playlist, 'shuffle on'
        shuffle = True
        radio.loadPlaylistIntoMPC(playlist, True)
        radio.launchPlaylist(playlist)
        radio.stopPlayback()
        exit(0)

    # Run the correct command for the options we selected
    if (smart):
        print 'Smart.'
        radio.smartHandleButtonPress(playlist)

    elif (time == ''):
        print 'Launch', playlist
        radio.launchPlaylist(playlist)

    else:
        print 'Launch', playlist, 'at', time
        radio.launchPlaylistAtNewSystemTime(playlist, time)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
if __name__ == "__main__":
    main(sys.argv[1:])