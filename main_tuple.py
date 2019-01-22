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
    The hosted organism is defined in a tuple object for 
    simple access and minimal RAM usage.
    Order of elements:
    parent1
    parent2
    gender
    color
    creation_time
'''
i_P1 = 0
i_P2 = 1
i_GENDER = 2
i_COLOR = 3
i_CREATION_TIME = 4

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
    Creates an organism from a comma-separated string value. 
    You can get the string value by calling org_to_string 
    on the org dict.
    '''
    repr_list = repr_string.split(',')
    org_tuple = (None if repr_list[i_P1] == 'None' else int(repr_list[i_P1]),
                 None if repr_list[i_P2] == 'None' else int(repr_list[i_P2]),
                 repr_list[i_GENDER],
                 repr_list[i_COLOR],
                 int(repr_list[i_CREATION_TIME])
                 )
    return org_tuple


def create_genesis_org():
    '''
    Create an organism without parents by randomly selecting 
    a trait from each trait list.
    creation_time is used as a unique identifier for the organism.
    '''
    org_tuple = (None,
                 None,
                 choice(('XX', 'XY')),
                 choice(('BB', 'Bb', 'bB', 'bb')),
                 ticks_ms()
                 )
    return org_tuple


def create_org_from_parents(parent1, parent2):
    '''
    Create an organism with parents by randomly selecting a gene 
    from each parent for each trait. 
    creation_time is used as a unique identifier for the organism.
    
    Returns False if the two parents have the same gender.
    '''
    if parent1[i_P1] == parent2[i_P2]:
        return False
    org_tuple = (get_org_hash(parent1),
                 get_org_hash(parent2),
                 combine_traits(parent1[i_GENDER], parent2[i_GENDER]),
                 combine_traits(parent1[i_COLOR], parent2[i_COLOR]),
                 ticks_ms()
                 )
    return org_tuple


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
    return ','.join([str(org[i_P1]),
                     str(org[i_P2]),
                     org[i_GENDER],
                     org[i_COLOR],
                     str(org[i_CREATION_TIME])])


def get_org_hash(org):
    if org is None:
        return None
    return hash(org)


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
                                                               org[i_GENDER],
                                                               org[i_COLOR]))
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
        display.show('G{}C{}'.format(genders[org[i_GENDER]][:1],
                                     colors[org[i_COLOR]][:1]))

    elif button_b.was_pressed():
        org = create_genesis_org()
        print(org)

    if state == 'RECV':
        msg = radio.receive()
        if msg is not None and msg[:4] == 'SREQ':
            print(msg)
            new_org = org_from_repr(msg[5:])
            if new_org[i_GENDER] != org[i_GENDER]:
                print('attempting reproduction')
                radio.send('SRSP|' + repr(org))
                org = create_org_from_parents(new_org, org)
                display.show(Image.YES)
                print('New organism {} created. {}'.format(get_org_hash(org),
                                                           org_to_string(org)))
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
