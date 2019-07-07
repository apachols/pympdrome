import aioserial
import asyncio

from lib import radio

# find port name by printing them all out
import serial.tools.list_ports
print([comport.device for comport in serial.tools.list_ports.comports()])

# current station
dial = -1

radio_station_list = {
    # left side - definitely workin
    0: '!STOP!',
    4: '!STOP!',
    8: '!STOP!',
    # bottom row - not sure if these will really work
    12: '!STOP!',
    13: '!STOP!',
    14: '!STOP!',
    15: '!STOP!',
    # real playlists
    1: 'rosie',
    2: 'fleshworldus',
    3: 'the_vaccine_underground',
    5: 'superstarvjs',
    6: 'cadaverous_mastication',
    7: 'darker3',
    9: 'mellowsexy',
    10: 'dubbysteps3',  # TODO
    11: 'adambient',  # TODO
    # marten's electronic explorations playlist?
    # anything from aury?
    # one more
}

def process_line(line: str):
    if 'PLAY' not in line:
        return
    try:
        parts = line.split(' ')
        selection = parts[1]
        handle_selection(selection)
    except Exception as exc:
        print(exc)

def handle_selection(selection: str):
    global dial
    station_index = int(selection)
    if station_index in radio_station_list and radio_station_list[station_index] == '!STOP!':
        print('Stop')
        radio.stopPlayback()
    elif station_index == dial:
        radio.skipToNextSong();
    else:
        selected_station = radio_station_list[station_index]
        print('', selected_station)
        radio.launchPlaylist(selected_station)
        dial = station_index

async def get_values(aioserial_instance: aioserial.AioSerial):
    while True:
        text = (await aioserial_instance.readline_async()).decode(errors='ignore')
        process_line(text)

def run():
    asyncio.run(get_values(aioserial.AioSerial(baudrate=115200, port='/dev/ttyACM0')))

run()
