import subprocess, re

#
##
####
# getFileDurationUsingFFProbe will return a song duration in milliseconds for a given fileUri
####
##
#

# return song duration in milliseconds for fileUri
def getFileDurationUsingFFProbe(fileUri):
    ffprobeOutput = subprocess.check_output(['ffprobe', fileUri], stderr=subprocess.STDOUT)
    return durationFromFFProbeResult(ffprobeOutput)

# parse multiline ffprobe output, return song duration in milliseconds
def durationFromFFProbeResult(ffprobeResult):
    ffprobeOutputLines = ffprobeResult.decode().split('\n')
    for aLine in ffprobeOutputLines:
        aLineStripped = aLine.strip()
        if aLineStripped.startswith('Duration'):
            totalMilliseconds = durationFromFFProbeDurationLine(aLineStripped)
            return totalMilliseconds
    raise FFProbeError("No duration found in FFProbe result")

# parse single line of ffprobe output, return song duration in milliseconds
def durationFromFFProbeDurationLine(line):
    matches = re.match(r"Duration: (\d\d):(\d\d):(\d+\.\d+)", line)
    if matches:
        hours, minutes, seconds = matches.groups(0)
        totalSeconds = int(hours) * 60 * 60 + int(minutes) * 60 + float(seconds)
        totalMilliseconds = int(totalSeconds*1000)
        return totalMilliseconds
    raise FFProbeError("Bad format for FFProbe duration line=" + line)

# error message
class FFProbeError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg
