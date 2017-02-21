# import subprocess
# asdf = subprocess.check_output(["mpc", "version"])
# print asdf

import sys, getopt, subprocess, re

def launch(playlist, time):
    print 'playlist is', playlist
    print 'time file is', time

    pathToFiles = '/Users/adamp/Music/MPD/'

    commandOutput = subprocess.check_output(["mpc", "ls", playlist])
    files = commandOutput.strip().split('\n')
    for aFile in files:
        fileUri = pathToFiles + aFile
        print "---------------------------------------"
        print 'HERE IS FFPROBE FOR', fileUri
        ffprobeOutput = subprocess.check_output(["ffprobe", fileUri], stderr=subprocess.STDOUT)
        ffprobeOutputLines = ffprobeOutput.split('\n')
        for aLine in ffprobeOutputLines:
            aLineStripped = aLine.strip()
            if aLineStripped.startswith('Duration'):
                matches = re.match(r"Duration: (\d\d):(\d\d):(\d+\.\d+)", aLineStripped)
                hours, minutes, seconds = matches.groups(0)
                print aLineStripped
                print hours, minutes, seconds
                totalSeconds = int(hours) * 60 * 60 + int(minutes) * 60 + float(seconds)
                print aFile, totalSeconds

def main(argv):
    help = 'launch.py -p <playlist> -t <time>'
    playlist = ''
    time = ''
    try:
        opts, args = getopt.getopt(argv,"hp:t:",["playlist=","time="])
    except getopt.GetoptError:
        print help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help
            sys.exit()
        elif opt in ("-p"): #, "--playlist"):
            playlist = arg
        elif opt in ("-t"): #, "--time"):
            time = arg

    launch(playlist, time)

if __name__ == "__main__":
    main(sys.argv[1:])