import aioserial
import asyncio

from lib import radio

# find port name by printing them all out
import serial.tools.list_ports
print([comport.device for comport in serial.tools.list_ports.comports()])

radio_station_list = {
    0: 'doduk',
    1: 'mid-air_thief',
    2: 'doduk',
    3: 'mid-air_thief',
    4: 'doduk',
    5: 'mid-air_thief',
    6: 'doduk',
    7: 'mid-air_thief',
    8: 'doduk',
    9: 'mid-air_thief',
    10: 'doduk',
    11: 'mid-air_thief',
    12: 'doduk',
    13: 'mid-air_thief',
    14: 'doduk',
    15: 'mid-air_thief',
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
    station_index = int(selection)
    selected_station = radio_station_list[station_index]
    print('', selected_station)
    radio.launchPlaylist(selected_station)

async def get_values(aioserial_instance: aioserial.AioSerial):
    while True:
        text = (await aioserial_instance.readline_async()).decode(errors='ignore')
        process_line(text)

def run():
    asyncio.run(get_values(aioserial.AioSerial(baudrate=115200, port='/dev/cu.usbmodem14201')))

run()
