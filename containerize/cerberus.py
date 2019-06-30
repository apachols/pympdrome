import signal
import subprocess
import os
from time import sleep
import sys

os.environ['PATH'] += os.pathsep + '/usr/local/bin'

blue_instance = subprocess.check_output([
    'docker', 'ps', '-aqf', 'name=pympdrome_blue_1'
], stderr=subprocess.STDOUT).strip()

red_instance = subprocess.check_output([
    'docker', 'ps', '-aqf', 'name=pympdrome_red_1'
], stderr=subprocess.STDOUT).strip()

green_instance = subprocess.check_output([
    'docker', 'ps', '-aqf', 'name=pympdrome_green_1'
], stderr=subprocess.STDOUT).strip()

blue = {
    "instance": blue_instance,
    "sink": None,
    "output": "Channel_1__Channel_2.2"
}

red = {
    "instance": red_instance,
    "sink": None,
    "output": "Front_Left__Front_Right"
}

green = {
    "instance": green_instance,
    "sink": None,
    "output": "Front_Left__Front_Right.2"
}

def fix_sink_routing():
    raw_pactl_out = subprocess.check_output([
        'pactl', 'list', 'sink-inputs'
    ], stderr=subprocess.STDOUT)

    all_sinks = [
        s
        for s in raw_pactl_out.split('\n\n') if 'org.PulseAudio.PulseAudio' not in s
    ]

    def get_sink_input_number(sink_input_str):
        return sink_input_str.split('\n')[0].split('#')[-1]

    for sink in all_sinks:
        if blue_instance in sink:
            blue['sink'] = get_sink_input_number(sink)
        if red_instance in sink:
            red['sink'] = get_sink_input_number(sink)
        if green_instance in sink:
            green['sink'] = get_sink_input_number(sink)

    def move_sink_input(sink_input_number, output_name):
        cmd = 'pactl move-sink-input {} \"{}\"'.format(sink_input_number, output_name)
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    if red.get('sink'):
        move_sink_input(red['sink'], red['output'])

    if blue.get('sink'):
        move_sink_input(blue['sink'], blue['output'])

    if green.get('sink'):
        move_sink_input(green['sink'], green['output'])


def pa_ctrl_changes(cmd):
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid
    )
    for stdout_line in iter(proc.stdout.readline, ""):
        if not 'remove' in stdout_line and 'sink-input #' in stdout_line:
            proc.stdout.close()
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            return stdout_line
        else:
            pass

def signal_handler(signal, frame):
    os.system("killall -9 pactl subscribe")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    out = ''
    for line in pa_ctrl_changes(["pactl", "subscribe"]):
        out += line
    print(out)
    sleep(0.125)

    try:
        fix_sink_routing()
    except Exception as exc:
        print("EXCEPTION")
        print(exc)
