from random import choice, randint
from abc import ABC, abstractmethod


class Trait(ABC):

    traits = {}

    def __init__(self, parent1_trait=None, parent2_trait=None, name='generic'):
        self.name = name
        if parent1_trait is None or parent2_trait is None:
            self.set_random_trait()
        else:
            self.trait = self.combine_traits(parent1_trait, parent2_trait)
        self.trait_value = self.traits[self.trait]

    def combine_traits(self, trait1, trait2, sort=True):
        """Joins two parent traits at random. A trait is defined as a 2-character string"""
        trait = [trait1[randint(0,1)], trait2[randint(0,1)]]
        if sort:
            return ''.join(sorted(trait))
        else:
            return ''.join(trait)

    def __repr__(self):
        return '{}: {}'.format(self.name, self.trait)

    def __str__(self):
        return '{}: {}'.format(self.trait, self.traits[self.trait])

    def set_random_trait(self):
        self.trait = choice(list(self.traits.keys()))

class Gender(Trait):
    """ A Trait subclass for genders. Only XX and XY are valid gender genotypes. """

    def __init__(self, parent1_gender=None, parent2_gender=None):
        self.traits = {'XX': 'Female', 'XY': 'Male'}
        super().__init__(parent1_gender,parent2_gender,name='Gender')
        self.trait = self.trait.upper()


class Color(Trait):
    """ A Trait subclass for colors. Color is either Blue or Yellow, with a capital B dominant gene"""

    def __init__(self, parent1_color=None, parent2_color=None):
        self.traits = {'BB': 'Blue', 'Bb': 'Blue', 'bb': 'Yellow', 'bB': 'Blue'}
        super().__init__(parent1_color, parent2_color, name='Color')
