from microbit import display, button_a, button_b
from os import listdir
from random import choice
from time import ticks_ms, ticks_add, sleep
import radio
import gc

maturity = 6  # time to reproduce in seconds
last_reproduction = 0

FILE = 'organism.txt'

state = 'RECV'


def combine_traits(trait1, trait2):
    trait = [choice(trait1), choice(trait2)]

    return ''.join(sorted(trait))


def org_from_repr(repr_string):
    repr_list = repr_string.split(',')
    org_dict = {
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
        'parent1': get_org_hash(parent1),
        'parent2': get_org_hash(parent2),
        'gender': combine_traits(parent1['gender'], parent2['gender']),
        'color': combine_traits(parent1['color'], parent2['color']),
        'creation_time': ticks_ms(),
        'generation': max(parent1['generation'], parent2['generation']) + 1
    }
    return org_dict


def write_string(s, filename):
    with open(filename, 'wt') as f:
        f.write(s)


def load_organism(filename):
    if filename not in listdir():
        print('File not found')
        return None
    with open(filename, 'rt') as f:
        loaded_org = org_from_repr(f.read())
    return loaded_org


def org_to_string(org):
    return ','.join([str(get_org_hash(org)),
                     org['gender'],
                     org['color'],
                     str(org['parent1']),
                     str(org['parent2']),
                     str(org['creation_time']),
                     str(org['generation'])])


def get_org_hash(org):
    return None if org is None else hash(','.join([str(org['creation_time']),
                                                   org['gender'],
                                                   org['color'],
                                                   str(org['parent1']),
                                                   str(org['parent2']),
                                                   str(org['generation'])
                                                   ]))


def print_org(org):
    print('''Organism {}
          Gen {}
          P1: {}
          P2: {}
          Gender: {}
          Color: {}
          Time: {}'''.format(get_org_hash(org),
                             org['generation'],
                             org['parent1'],
                             org['parent2'],
                             org['gender'],
                             org['color'],
                             org['creation_time']
                             ))


print('loading...')

org = load_organism(FILE)
if org is None:
    print('could not load org from file')
    org = create_genesis_org()
    write_string(org_to_string(org), FILE)
print_org(org)

radio.on()
radio.config(length=100)
while True:
    display.show(state[0], delay=100, wait=False)
    gc.collect()

    if ticks_ms() < ticks_add(last_reproduction, maturity * 1000):
        state = 'WAIT'
    elif state == 'WAIT':
        state = 'RECV'

    if button_a.is_pressed() and button_b.is_pressed():
        org = create_genesis_org()
        write_string(org_to_string(org), FILE)
        print_org(org)
        sleep(1)

    elif button_a.was_pressed():
        display.scroll('G:{} C:{}'.format(org['gender'], org['color']))


    elif button_b.was_pressed() and state == 'RECV':
        state = 'SEND'
        msg = 'SREQ|' + org_to_string(org)
        radio.send(msg)

    if state == 'RECV':
        msg = radio.receive()
        if msg is not None and msg[:4] == 'SREQ':
            new_org = org_from_repr(msg[5:])
            if new_org['gender'] != org['gender']:
                print('attempting reproduction')
                print('Parent 1:')
                print_org(org)
                print('Parent 2:')
                print_org(new_org)
                radio.send('SRSP|' + org_to_string(org))
                org = create_org_from_parents(new_org, org)
                print('Offspring:')
                print_org(org)
                write_string(org_to_string(org), FILE)
                display.show('+ ')
                last_reproduction = ticks_ms()

            else:
                display.show('X ')
                print('ignoring same-gender reproduction request')
    elif state == 'SEND':
        deadline = ticks_add(ticks_ms(), 500)
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
                radio.send('SACK|' + str(get_org_hash(org)))
                display.show('+ ')
                state = 'RECV'
                last_reproduction = ticks_ms()
                break
        if state == 'SEND':
            print('message send timeout. No org received')
            display.show('X ')
            state = 'RECV'

    # print((gc.mem_free(),))
