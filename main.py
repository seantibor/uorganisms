from microbit import display, button_a, button_b
from os import listdir
from random import choice
from time import ticks_ms, ticks_add
import radio

genders = {'XX': 'Female', 'XY': 'Male'}
colors = {'BB': 'Blue', 'Bb': 'Blue', 'bB': 'Blue', 'bb': 'Yellow'}
FILE = 'bob.json'

org = ''
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


class Organism(object):
    """
    Represents a micro:bit organism with specific traits.
    """

    def __init__(self, parent1=None, parent2=None, gender=None,
                 color=None, parent1_hash=None, parent2_hash=None,
                 creation_time=None):
        # case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None if parent1_hash is None else parent1_hash
            self.parent2 = None if parent2_hash is None else parent2_hash
            self.gender = choice(('XX', 'XY')) if gender is None else gender
            self.color = choice(('BB', 'Bb', 'bB', 'bb')) if color is None else color
        else:  # for generation 2+
            self.parent1 = hash(parent1)
            self.parent2 = hash(parent2)
            if parent1.gender == parent2.gender:
                raise Exception('parents must have different genders')
            else:
                self.gender = combine_traits(parent1.gender, parent2.gender, sort=True)
            self.color = combine_traits(parent1.color,
                                        parent2.color, sort=False)

        self.female = self.gender == 'XY'
        self.creation_time = ticks_ms() if creation_time is None else creation_time

    def __repr__(self):
        return ','.join([str(self.__hash__()), self.gender, self.color, str(self.parent1), str(self.parent2),
                         str(self.creation_time)])

    def __hash__(self):
        if self.parent1 is None or self.parent2 is None:
            return hash(str(self.creation_time) + self.gender + self.color)
        else:
            return hash(str(self.creation_time) + self.gender + self.color + str(self.parent1) + str(self.parent2))

    @classmethod
    def org_from_repr(cls, repr_string):
        repr_list = repr_string.split(',')
        parent1 = None if repr_list[3] == 'None' else int(repr_list[3])
        parent2 = None if repr_list[4] == 'None' else int(repr_list[4])
        return Organism(gender=repr_list[1],
                        color=repr_list[2],
                        parent1_hash=parent1,
                        parent2_hash=parent2,
                        creation_time=repr_list[5])


def write_string(s, filename):
    with open(filename, 'wt') as f:
        f.write(s)


def load_organism(filename):
    if filename not in listdir():
        print('File not found')
        return None
    with open(filename, 'rt') as f:
        loaded_org = Organism.org_from_repr(f.read())
    return loaded_org


"""
Start of main program code
"""

print('loading...')

try:
    org = load_organism(FILE)
    if org is None:
        print('could not load org from file')
    print('Organism {} loaded with {} gender and {} color.'.format(hash(org), org.gender, org.color))
    display.scroll('Loaded', wait=False)
except AttributeError:
    display.scroll('NF')
    print('Organism not found. Creating new organism and writing it to file')
    org = Organism()
    write_string(repr(org), FILE)
    display.scroll('Written', wait=False)
    print('Organism {} written with {} gender and {} color.'.format(hash(org), org.gender, org.color))
    print(repr(org))

radio.on()
radio.config(length=100)

while True:
    display.show(state[0], delay=100, wait=False)
    if button_a.was_pressed():
        state = 'SEND'
        msg = 'SREQ|' + repr(org)
        print(msg)
        radio.send(msg)

    if button_b.was_pressed():
        org = Organism()
        print(repr(org))

    if state == 'RECV':
        msg = radio.receive()
        if msg is not None and msg[:4] == 'SREQ':
            print(msg)
            new_org = Organism.org_from_repr(msg[5:])
            if new_org.gender != org.gender:
                print('attempting reproduction')
                radio.send('SRSP|' + repr(org))
                org = Organism(parent1=new_org, parent2=org)
                print('New organism {} created. {}'.format(hash(org), repr(org)))
            else:
                print('ignoring same-gender reproduction request')
    elif state == 'SEND':
        deadline = ticks_add(ticks_ms(), 500)
        while ticks_ms() < deadline:
            msg = radio.receive()
            display.show('S')
            if msg is not None and msg[:4] == 'SRSP':
                print(msg)
                new_org = Organism.org_from_repr(msg[5:])
                org = Organism(parent1=org, parent2=new_org)
                radio.send('SACK|' + str(hash(org)))
                state = 'RECV'
                break
        if state == 'SEND':
            print('message send timeout. No org received')
            state = 'RECV'
