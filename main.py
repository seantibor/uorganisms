from microbit import display
from os import listdir
from random import choice, randint

genders = {'XX': 'Female', 'XY': 'Male'}
colors = {'BB': 'Blue', 'Bb': 'Blue', 'bB': 'Blue', 'bb': 'Yellow'}
FILE = 'bob.json'


def main():
    print('loading...')
    try:
        org = load_organism(FILE)
        if org is None:
            print('could not load org from file')
        print('Organism {} loaded with {} gender and {} color.'.format(org.name, org.traits['gender'],
                                                                       org.traits['color']))
        display.scroll('Loaded')
    except AttributeError:
        display.scroll('NF')
        print('Organism not found. Creating new organism and writing it to file')
        org = Organism('bob', None, None)
        write_string(repr(org), FILE)
        display.scroll('Written')
        print('Organism {} written with {} gender and {} color.'.format(org.name, org.traits['gender'],
                                                                        org.traits['color']))


def hash_string(s):
    """
    Hash a string using the djb2 algorithm found at https://gist.github.com/mengzhuo/180cd6be8ba9e2743753
    :param s:
    :return hash value:
    """
    hash = 5381
    for x in s:
        hash = ((hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF


def combine_traits(trait1, trait2, sort=True):
    """Joins two parent traits at random. A trait is defined as a 2-character string"""
    trait = [trait1[randint(0, 1)], trait2[randint(0, 1)]]
    if sort:
        return ''.join(sorted(trait))
    else:
        return ''.join(trait)


class Organism(object):
    """
    Represents a micro:bit organism with specific traits.
    """
    traits = {}

    def __init__(self, name, parent1, parent2):
        self.name = name

        # case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None
            self.parent2 = None
            self.traits['gender'] = choice(('XX', 'XY'))
            self.traits['color'] = choice(('BB', 'Bb', 'bB', 'bb'))
            self.hash = hash_string(self.name + str(self.traits))
        else:  # for generation 2+
            self.parent1 = parent1.hash
            self.parent2 = parent2.hash
            if parent1.traits['gender'] == parent2.traits['gender']:
                raise Exception('parents must have different genders')
            else:
                self.traits['gender'] = combine_traits(parent1.traits['gender'], parent2.traits['gender'], sort=True)
            self.traits['color'] = combine_traits(parent1.traits['color'].trait, parent2.traits['color'].trait,
                                                  sort=False)
            self.hash = hash_string(self.name + self.parent1 + self.parent2 + str(self.traits))

        self.female = True if self.traits['gender'] == 'XY' else False

    def __repr__(self):
        return str({'name': self.name, 'hash': self.hash, 'parent1': self.parent1, 'parent2': self.parent2,
                    'traits': self.traits})

    def update_from_repr(self, repr_string):
        org_dict = eval(repr_string)
        print('org_dict loaded')
        self.name = org_dict['name']
        self.parent1 = org_dict['parent1']
        self.parent2 = org_dict['parent2']
        self.traits['color'] = org_dict['traits']['color']
        self.traits['gender'] = org_dict['traits']['gender']


def write_string(repr_string, filename):
    with open(filename, 'wt') as f:
        f.write(repr_string)
        f.close()


def load_organism(filename):
    if filename not in listdir():
        print('File not found')
        return None
    with open(filename, 'rt') as f:
        try:
            repr_string = f.read()
            loaded_org = Organism('_', None, None)
            loaded_org.update_from_repr(repr_string)
            return loaded_org
        except ValueError:
            print('Could not load organism from file with name {}.'.format(filename))
            return None
        finally:
            f.close()
