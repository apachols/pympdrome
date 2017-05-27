import pickle, os, time

TIME_FILE_NAME = '/Users/adamp/.mpd/hypnotime'

#
##
####
# system utils:
#  - getCurrentSystemTimeMs() returns system time in milliseconds
#  - reset() starts system time over at zero
####
##
#

def readTimeFile():
    try:
        with open(TIME_FILE_NAME, 'rb') as filehandle:
            return pickle.load(filehandle)
    except Exception as e:
        return None

def writeTimeFile(currentTimeMs):
    with open(TIME_FILE_NAME, 'wb') as filehandle:
        pickle.dump(currentTimeMs, filehandle)

def getCurrentSystemTimeMs():
    systemStartTimeMs = readTimeFile()

    # time() returns a floating point number in whole seconds since the epoch
    intCurrentTimeMs = int(time.time() * 1000)

    if (systemStartTimeMs is None):
        writeTimeFile(intCurrentTimeMs)
        return 0
    else:
        return intCurrentTimeMs - systemStartTimeMs

#
# TODO MORE STUFF HERE
#
def reset():
    os.remove(TIME_FILE_NAME)