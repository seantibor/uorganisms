from microbit import display, button_a
from os import listdir
from random import choice, randint
import time
import radio

genders = {'XX': 'Female', 'XY': 'Male'}
colors = {'BB': 'Blue', 'Bb': 'Blue', 'bB': 'Blue', 'bb': 'Yellow'}
FILE = 'bob.json'

org = ''
state = 'RECV'


def start():
    print('loading...')
    global org

    try:
        org = load_organism(FILE)
        if org is None:
            print('could not load org from file')
        print('Organism {} loaded with {} gender and {} color.'.format(
            org.name, org.gender, org.color))
        display.scroll('Loaded', wait=False)
    except AttributeError:
        display.scroll('NF')
        print('Organism not found. Creating new organism and writing it to file')
        org = Organism('bob', None, None)
        write_string(repr(org), FILE)
        display.scroll('Written')
        print('Organism {} written with {} gender and {} color.'.format(org.name, org.gender, org.color))
        print(repr(org))

    radio.on()


def loop():
    global org, state

    if button_a.was_pressed():
        state = 'SEND'
        msg = 'SREQ|' + repr(org)
        print(msg)
        radio.send(msg)

    if state == 'RECV':
        msg = radio.receive()
        if msg is not None:
            print(msg)
            new_org = Organism('received_parent', None, None)
            new_org.update_from_repr(eval(msg[5:]))
            if new_org.gender != org.gender:
                print('attempting reproduction')
                radio.send('SRSP|' + repr(org))
                org = Organism('offspring', new_org, org)
    elif state == 'SEND':
        deadline = time.ticks_add(time.ticks_ms(), 500)
        while time.ticks_ms() < deadline:
            msg = radio.receive()
            if msg is not None and msg[:4] == 'SRSP':
                print(msg)
                new_org = Organism('new bob', None, None)
                new_org.update_from_repr(eval(msg[5:]))
                org = Organism('new bob', org, new_org)
                radio.send('SACK|' + str(org.hash))
                state = 'RECV'
                break
        if state == 'SEND':
            print('message send timeout. No org received')
            state = 'RECV'


def hash_string(s):
    """
    Hash a string using the djb2 algorithm found at 
    https://gist.github.com/mengzhuo/180cd6be8ba9e2743753
    :param s:
    :return hash value:
    """
    hash = 5381
    for x in s:
        hash = ((hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF


def combine_traits(trait1, trait2, sort=True):
    """
    Joins two parent traits at random. 
    A trait is defined as a 2-character string
    """
    trait = [trait1[randint(0, 1)], trait2[randint(0, 1)]]
    if sort:
        return ''.join(sorted(trait))
    else:
        return ''.join(trait)


class Organism(object):
    """
    Represents a micro:bit organism with specific traits.
    """

    def __init__(self, name, parent1, parent2):
        self.name = name

        # case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None
            self.parent2 = None
            self.gender = choice(('XX', 'XY'))
            self.color = choice(('BB', 'Bb', 'bB', 'bb'))
            self.hash = hash_string(self.name + self.gender + self.color)
        else:  # for generation 2+
            self.parent1 = parent1.hash
            self.parent2 = parent2.hash
            if parent1.gender == parent2.gender:
                raise Exception('parents must have different genders')
            else:
                self.gender = combine_traits(parent1.gender, parent2.gender, sort=True)
            self.color = combine_traits(parent1.color,
                                        parent2.color, sort=False)
            self.hash = hash_string(self.name + self.parent1 + self.parent2 + self.gender + self.color)

        self.female = self.gender == 'XY'

    def __repr__(self):
        return str({'name': self.name, 'hash': self.hash,
                    'parent1': self.parent1, 'parent2': self.parent2,
                    'gender': self.gender, 'color': self.color})

    def update_from_repr(self, repr_string):
        org_dict = eval(repr_string)
        print('org_dict loaded')
        self.name = org_dict['name']
        self.parent1 = org_dict['parent1']
        self.parent2 = org_dict['parent2']
        self.color = org_dict['color']
        self.gender = org_dict['gender']


def write_string(repr_string, filename):
    with open(filename, 'wt') as f:
        f.write(repr_string)


def load_organism(filename):
    if filename not in listdir():
        print('File not found')
        return None
    with open(filename, 'rt') as f:
        repr_string = f.read()
        loaded_org = Organism('_', None, None)
        loaded_org.update_from_repr(repr_string)
        return loaded_org


if __name__ == '__main__':
    start()
    while True:
        loop()
