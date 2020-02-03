'''
This module will listen for traffic on the microbit radio and log interactions to a file.
Reproduction events will be recorded in a Google Sheet.
'''

import serial
import datetime
import time
import pygsheets
from pathlib import Path

default_port = '/dev/tty.usbmodem14102'
default_baud = 115200

csv_headers = ["Command", "Organism hash", "Gender Trait", "Color Trait", "Parent 1", "Parent 2", "Sender Time", "Generation Number", "System Timestamp"]

log_file = None

def get_output_csv(file_prefix:str='uorganism_log', file_suffix:str='csv'):
    file_date = datetime.now()
    file_path = Path(f"{file_prefix}_{file_date.isoformat()}_.{file_suffix}")

    with open(file_path, 'w') as output_file:
        output_file.write(','.join(csv_headers))
        yield output_file


def get_serial(port:str=default_port, baud:int=default_baud) -> serial.Serial:
    ''' Opens a new serial connection
    params:
        port - the logical port on your computer for the microbit
        baud - the serial baud rate of the connect, defaults to 115200
    '''
    port = Path(port)
    s = serial.Serial(str(port))
    s.baudrate = baud
    return s

def read_message(msg):
    if '|' not in msg:
        print('msg')
        return

    command, payload = msg.split('|')
    if command == 'SREQ':
        handle_request(payload)
    elif command == 'SRSP':
        handle_response(payload)
    elif command == 'SACK':
        handle_acknowledgement(payload)
    else:
        print(f'Encountered unknown command: {command}')

def log_to_gsheets(organism, sheet):
    '''
        Logs a single organism to the specified Google Worksheet
    '''
    pass

def log_to_file(organism, file):
    '''
        Logs a single organism to the specified csv file
    '''
    pass

def get_organism_sheet(sheet_name:str, wks_name:str) -> pygsheets.Worksheet:
    '''
        Gets a Google Sheet and returns a single worksheet by name.
        If the spreadsheet or worksheet do not exist, it will create them.
    '''
    pass
    
def handle_request(request):
    '''
    Handles a reproduction request. Will log request to file. Does not write to GSheets
    '''
    print('Request Received')
    pass

def handle_response(response):
    print('Response Received')
    pass

def handle_acknowledgement(ack):
    print('Acknowledgement Received')
    pass

def main():
    global log_file

    s = get_serial()
    log_file = get_output_csv()

    while True:
        data = s.readline()
        data = data.decode('utf-8')
        data = data.strip()
        read_message(data)
        print(data)

if __name__ == '__main__':
    main()