from microbit import display, button_a, button_b, Image
from os import listdir
from random import choice, randint
from time import ticks_ms, sleep
import radio
from gc import collect

maturity = randint(10, 30)  # time to reproduce in seconds
last_reproduction = 0

FILE = 'organism.txt'

state = "WAIT"

def combine_traits(trait1, trait2):
    trait = [choice(trait1), choice(trait2)]
    return ''.join(sorted(trait))


def org_from_repr(repr_string):
    repr_list = repr_string.split(',')
    if not repr_list[6].isnumeric():
        repr_list[6] = 0
    org_dict = {
        'id': repr_list[0],
        'parent1': None if repr_list[3] == 'None' else int(repr_list[3]),
        'parent2': None if repr_list[4] == 'None' else int(repr_list[4]),
        'gender': repr_list[1],
        'color': repr_list[2],
        'creation_time': int(repr_list[5]),
        'generation': int(repr_list[6])
    }

    return org_dict


def create_genesis_org():
    org_dict = {
        'id': get_org_id(),
        'parent1': None,
        'parent2': None,
        'gender': choice(('XX', 'XY')),
        'color': choice(('BB', 'Bb', 'bB', 'bb')),
        'creation_time': ticks_ms(),
        'generation': 0
    }
    return org_dict


def create_org_from_parents(parent1, parent2):
    if parent1['gender'] == parent2['gender']:
        return False
    org_dict = {
        'id': get_org_id(),
        'parent1': parent1['id'],
        'parent2': parent2['id'],
        'gender': combine_traits(parent1['gender'], parent2['gender']),
        'color': combine_traits(parent1['color'], parent2['color']),
        'creation_time': ticks_ms(),
        'generation': max(parent1['generation'], parent2['generation']) + 1
    }
    if org_dict['generation'] is None:
        org_dict['generation'] = 0
    return org_dict


def write_string(s, filename):
    with open(filename, 'wt') as f:
        f.write(s)


def load_organism(filename):
    if filename not in listdir():
        return None
    with open(filename, 'rt') as f:
        loaded_org = org_from_repr(f.read())
    return loaded_org


def org_to_string(org):
    return ','.join([str(value) for value in org.values()])

def get_org_id():
    return randint(10000,100000)


def print_org(org):
    print('''Organism {}
          Gen {}
          P1: {}
          P2: {}
          Gender: {}
          Color: {}
          Time: {}'''.format(org['id'],
                             org['generation'],
                             org['parent1'],
                             org['parent2'],
                             org['gender'],
                             org['color'],
                             org['creation_time']
                             ))


org = load_organism(FILE)
if org is None:
    org = create_genesis_org()
    write_string(org_to_string(org), FILE)
print_org(org)

radio.on()
radio.config(length=40)
while True:
    
    display.show(state[0], delay=100, wait=False)    
    msg = radio.receive()

    if msg == 'LOCK':
        state = msg
        continue
    elif state == 'LOCK' and msg == 'UNLOCK':
        state = 'WAIT'

    if state == 'LOCK':
        continue
    
    if msg == 'RESET':
        org = create_genesis_org()
        print_org(org)
        write_string(org_to_string(org), FILE)
        
    collect()

    if ticks_ms() < last_reproduction + maturity * 1000:
        state = 'WAIT'
    elif state == 'WAIT':
        state = 'RECV'

    elif button_a.was_pressed():
        display.scroll('G:{} C:{}'.format(org['gender'], org['color']))

    elif button_b.was_pressed() and state == 'RECV':
        state = 'SEND'
        msg = 'SREQ|{}'.format(org_to_string(org))
        radio.send(msg)

    if state == 'RECV':
        if msg is not None and msg[:4] == 'SREQ' and randint(1,3) == 1:
            new_org = org_from_repr(msg[5:])
            if new_org['gender'] != org['gender']:
                print('Parent 1:')
                print_org(org)
                print('Parent 2:')
                print_org(new_org)
                radio.send('SRSP|{}'.format(org_to_string(org)))
                org = create_org_from_parents(new_org, org)
                print('Offspring:')
                print_org(org)
                write_string(org_to_string(org), FILE)
                display.show(Image.YES, wait=True, clear=True)
                last_reproduction = ticks_ms()

            else:
                display.show(Image.NO, wait=True, clear=True)
    elif state == 'SEND':
        deadline = ticks_ms() + 500
        while ticks_ms() < deadline:
            msg = radio.receive()
            if msg is not None and msg[:4] == 'SRSP':
                new_org = org_from_repr(msg[5:])
                print('Parent 1:')
                print_org(org)
                print('Parent 2:')
                print_org(new_org)
                org = create_org_from_parents(org, new_org)
                write_string(org_to_string(org), FILE)
                print('Offspring:')
                print_org(org)
                radio.send('SACK|{}'.format(org_to_string(org)))
                display.show(Image.YES, wait=True, clear=True)
                state = 'RECV'
                last_reproduction = ticks_ms()
                break
        if state == 'SEND':
            display.show(Image.NO, wait=True, clear=True)
            state = 'RECV'
