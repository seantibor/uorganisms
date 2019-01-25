from microbit import display, button_a, button_b, Image
from os import listdir
from random import choice
from time import ticks_ms, ticks_add
import radio

# import gc

# Maps traits to human-readable values
genders = {'XX': 'Female', 'XY': 'Male'}
colors = {'BB': 'Blue', 'Bb': 'Blue', 'bB': 'Blue', 'bb': 'Yellow'}
orgs = {}

''' 
    Filename for storing organism on microbit. 
    Will not be preserved when the microbit is flashed.
'''
FILE = 'organism.txt'
ORG_FILE = 'orgs.txt'

''' 
    The hosted organism is defined in a dictionary object for 
    simple access and minimal RAM usage.
'''
org = {'parent1': None,
       'parent2': None,
       'gender': None,
       'color': None,
       'creation_time': None
       }
'''
    The current communications state of the microbit.
    Possible values:
    SEND - broadcast a reproduction request and listen for a response
    RECV - wait for a viable reproduction request
'''
state = 'RECV'


def combine_traits(trait1, trait2, sort=True):
    """
    Joins two parent traits at random. 
    A trait is defined as a 2-character string
    """
    trait = [choice(trait1), choice(trait2)]
    if sort:
        return ''.join(sorted(trait))
    else:
        return ''.join(trait)


def org_from_repr(repr_string):
    '''
    Creates an organism from a comma-separated string value. You can get the string 
    value by calling org_to_string on the org dict.
    '''
    repr_list = repr_string.split(',')
    org_dict = {
        'parent1': None if repr_list[3] == 'None' else int(repr_list[3]),
        'parent2': None if repr_list[4] == 'None' else int(repr_list[4]),
        'gender': repr_list[1],
        'color': repr_list[2],
        'creation_time': int(repr_list[5])
    }
    return org_dict


def create_genesis_org():
    '''
    Create an organism without parents by randomly selecting a trait from each trait list.
    creation_time is used as a unique identifier for the organism.
    '''
    org_dict = {
        'parent1': None,
        'parent2': None,
        'gender': choice(('XX', 'XY')),
        'color': choice(('BB', 'Bb', 'bB', 'bb')),
        'creation_time': ticks_ms()
    }
    return org_dict


def create_org_from_parents(parent1, parent2):
    '''
    Create an organism with parents by randomly selecting a gene 
    from each parent for each trait. 
    creation_time is used as a unique identifier for the organism.
    
    Returns False if the two parents have the same gender.
    '''
    if parent1['gender'] == parent2['gender']:
        return False
    org_dict = {
        'parent1': parent1,
        'parent2': parent2,
        'gender': combine_traits(parent1['gender'], parent2['gender']),
        'color': combine_traits(parent1['color'], parent2['color']),
        'creation_time': ticks_ms()
    }
    return org_dict


def write_string(s, filename):
    ''' 
        Writes a string to the filename provided on the microbit file system
    '''
    with open(filename, 'wt') as f:
        f.write(s)


def load_organism(filename):
    ''' 
        Attempts to load an organism from the file system 
        using the filename provided.
        
        Returns a dict object representing the organism 
        or None if the file is not found
    '''
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
                     str(get_org_hash(org['parent1'])),
                     str(get_org_hash(org['parent2'])),
                     str(org['creation_time'])])


def get_org_hash(org):
    if org is None:
        return None
    return hash(','.join(org))


"""
Start of main program code
"""

print('loading...')

org = load_organism(FILE)
if org is None:
    print('could not load org from file')
    org = create_genesis_org()
    write_string(org_to_string(org), FILE)
print('Organism {} loaded with {} gender and {} color.'.format(get_org_hash(org),
                                                               org['gender'],
                                                               org['color']))
display.scroll('Loaded', wait=False)

radio.on()
radio.config(length=100)
while True:
    display.show(state[0], delay=100, wait=False)

    if button_a.is_pressed() and button_b.is_pressed():
        state = 'SEND'
        msg = 'SREQ|' + org_to_string(org)
        print(msg)
        radio.send(msg)

    elif button_a.was_pressed():
        print('showing object')
        display.show('G{}C{}'.format(genders[org['gender']][:1], colors[org['color']][:1]))

    elif button_b.was_pressed():
        org = create_genesis_org()
        print(org)

    if state == 'RECV':
        msg = radio.receive()
        if msg is not None and msg[:4] == 'SREQ':
            print(msg)
            new_org = org_from_repr(msg[5:])
            if new_org['gender'] != org['gender']:
                print('attempting reproduction')
                radio.send('SRSP|' + repr(org))
                org = create_org_from_parents(new_org, org)
                display.show(Image.YES)
                print('New organism {} created. {}'.format(get_org_hash(org),
                                                           repr(org)))
            else:
                display.show(Image.NO)
                print('ignoring same-gender reproduction request')
    elif state == 'SEND':
        deadline = ticks_add(ticks_ms(), 500)
        while ticks_ms() < deadline:
            msg = radio.receive()
            if msg is not None and msg[:4] == 'SRSP':
                print(msg)
                new_org = org_from_repr(msg[5:])
                org = create_org_from_parents(org, new_org)
                radio.send('SACK|' + str(hash(org)))
                display.show(Image.YES)
                state = 'RECV'
                break
        if state == 'SEND':
            print('message send timeout. No org received')
            display.show(Image.NO)
            state = 'RECV'

    # print((gc.mem_free(),))
