'''
This module will listen for traffic on the microbit radio and log interactions to a file.
Reproduction events will be recorded in a Google Sheet.
'''

import serial
import datetime
import time
import pygsheets
from pathlib import Path
from os import path
import click
import bullet

import asyncio
import aioserial
import queue
import concurrent.futures

q: queue.Queue = queue.Queue(1000)

default_port = '/dev/tty.usbmodem141402'
default_baud = 115200
client = pygsheets.authorize()

organisms = {}

csv_headers = ["Command", "Organism hash", "Gender Trait", "Color Trait", "Parent 1", "Parent 2", "Sender Time", "Generation Number", "System Timestamp"]
sheet_headers = csv_headers[1:]

file_date = datetime.datetime.now()
file_path = Path(f"organism_log_{file_date.isoformat()}.csv")

google_worksheet = None

def get_serial(port:str=default_port, baud:int=default_baud) -> aioserial.AioSerial:
    ''' Opens a new serial connection
    params:
        port - the logical port on your computer for the microbit
        baud - the serial baud rate of the connect, defaults to 115200
    '''
    s: aioserial.AioSerial = aioserial.AioSerial(port=port, baudrate=baud)
    return s

def read_message(msg):
    if '|' not in msg:
        print(msg)
        return

    command, payload = msg.split('|')
    if command in ('SREQ','SRSP','SACK'):
        log_organism(payload)
        log_to_file(msg.replace('|', ','))
    else:
        print(f'Encountered unknown command: {command}')

def log_to_gsheets(organism, sheet):
    '''
        Logs a single organism to the specified Google Worksheet
    '''
    organism_values = organism.split(',')
    timestamp = datetime.datetime.utcnow()
    organism_values.append(timestamp.strftime('%m/%d/%Y %H:%M:%S'))
    sheet.append_table(organism_values)
        

def log_to_file(organism):

    # add the current UTC time as an ISO string
    timestamp = datetime.datetime.utcnow()
    timestamp = timestamp.isoformat()
    organism = organism.split(',')
    if len(organism) < len(csv_headers):
        organism.append(timestamp)
    org_string = ','.join(organism)
    # append the string to the file.
    if not path.exists(file_path):
        with open(file_path, 'w') as log_file:
            log_file.write(','.join(csv_headers))
            log_file.write('\n')

    with open(file_path, 'a') as log_file:
        log_file.write(org_string)
        log_file.write('\n')

def get_organism_sheet(sheet_name:str, wks_name:str) -> pygsheets.Worksheet:
    '''
        Gets a Google Sheet and returns a single worksheet by name.
        If the spreadsheet or worksheet do not exist, it will create them.
    '''
    sh = get_spreadsheet(sheet_name)
    
    try:
        wks = sh.worksheet_by_title(wks_name)
    except pygsheets.WorksheetNotFound:
        wks = sh.add_worksheet(wks_name)
        wks.insert_rows(0, values=sheet_headers)
    
    return wks

def get_spreadsheet(sheet_name=None):
    gc = pygsheets.authorize()

    try:
        sh = gc.open(sheet_name)
    except pygsheets.SpreadsheetNotFound:
        if sheet_name:
            query = f'name contains "{sheet_name.split()[0].lower()}"'
        else:
            query = ""
        spreadsheets = gc.spreadsheet_titles(query=query)
        while not spreadsheets:
            if bullet.YesNo(prompt="Could not find spreadsheet. Do you want to create one?"):
                return gc.create(sheet_name)
            prompt = bullet.Input(
                prompt="Here are the sheets we found: Enter your query: "
            )
            query = prompt.launch()
            spreadsheets = gc.spreadsheet_titles(
                query=f'name contains "{query.lower()}"'
            )
        prompt = bullet.Bullet(
            choices=spreadsheets, prompt="Spreadsheet Names (Closest Match):"
        )
        sheet_name = prompt.launch()
        sh = gc.open(sheet_name)

    return sh

def handle_request(request):
    '''
    Handles a reproduction request. Will log request to file. Does not write to GSheets
    '''
    print('Request Received')
    log_to_file("Request," + request)
    log_organism(request)

def log_organism(organism):
    organism_id = int(organism.split(',')[0])
    if organism_id not in organisms:
        organisms[organism_id] = organism
        try: 
            log_to_gsheets(organism, google_worksheet)
        except ConnectionResetError:
            google_worksheet.client = pygsheets.authorize()
            log_to_gsheets(organism, google_worksheet)
        print(f"Logged organism {organism_id} to Google Sheets")
    else:
        print(f"Organism {organism_id} already known. Not logging.")

def handle_response(response):
    print('Response Received')
    log_to_file("Response," + response)
    log_organism(response)

def handle_acknowledgement(ack):
    print('Acknowledgement Received')
    log_to_file("Acknowledgement," + ack)
    log_organism(ack)

async def readline_and_put_to_queue(
        aioserial_instance: aioserial.AioSerial,
        q: queue.Queue):
    while True:
        q.put(await aioserial_instance.readline_async())

async def process_queue(q: queue.Queue):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        while True:
            line: bytes = await asyncio.get_running_loop().run_in_executor(
                    executor, q.get)
            line = line.decode('utf-8')
            line = line.strip()
            print(line)
            read_message(line)
            q.task_done()

@click.command()
@click.option('-p', '--serial-port', default=default_port)
@click.option('-b', '--baud-rate', default=default_baud)
@click.argument('sheet_name')
@click.argument('worksheet')
def main(sheet_name, worksheet, serial_port, baud_rate):

    print(f'attempting to open {serial_port} at {baud_rate}')
    s = get_serial(port=serial_port, baud=baud_rate)
    print(f'Serial port {serial_port} opened')
    global google_worksheet

    print(f'attempting to open google spreadsheet {sheet_name} with worksheet {worksheet}')
    if not google_worksheet:
        google_worksheet = get_organism_sheet(sheet_name, worksheet)
    print(f'google spreadsheet {sheet_name} with worksheet {worksheet} opened')

    asyncio.run(asyncio.wait([
        readline_and_put_to_queue(s, q),
        process_queue(q),
    ]))

if __name__ == '__main__':
    main()