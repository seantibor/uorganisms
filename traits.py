from random import choice, randint


# from abc import ABC, abstractmethod


class Trait(object):

    traits = {}

    def __init__(self, parent1_trait=None, parent2_trait=None, name="generic"):
        self.name = name
        if parent1_trait is None or parent2_trait is None:
            self.set_random_trait()
        else:
            self.trait = self.combine_traits(parent1_trait, parent2_trait)
        self.trait_value = self.traits[self.trait]

    def combine_traits(self, trait1, trait2, sort=True):
        """Joins two parent traits at random. A trait is defined as a 2-character string"""
        trait = [choice(trait1), choice(trait2)]
        if sort:
            return "".join(sorted(trait))
        else:
            return "".join(trait)

    def __repr__(self):
        return str(
            {"name": self.name, "trait": self.trait, "trait_value": self.trait_value}
        )

    def __str__(self):
        return f"{self.trait}: {self.traits[self.trait]}"

    def set_random_trait(self):
        pass


class Gender(Trait):
    """ A Trait subclass for genders. Only XX and XY are valid gender genotypes. """

    traits = {"XX": "Female", "XY": "Male"}
    trait_keys = list(traits.keys())

    def __init__(self, parent1_gender=None, parent2_gender=None):
        super().__init__(parent1_gender, parent2_gender, name="Gender")
        self.trait = self.trait.upper()

    def set_random_trait(self):
        self.trait = choice(self.trait_keys)
        self.trait_value = self.traits[self.trait]


class Color(Trait):
    """ A Trait subclass for colors. Color is either Blue or Yellow, with a capital B dominant gene"""

    traits = {"BB": "Blue", "Bb": "Blue", "bb": "Yellow", "bB": "Blue"}
    trait_keys = list(traits.keys())

    def __init__(self, parent1_color=None, parent2_color=None):
        super().__init__(parent1_color, parent2_color, name="Color")

    def set_random_trait(self):
        self.trait = choice(self.trait_keys)
        self.trait_value = self.traits[self.trait]


class GenericTrait(Trait):
    """ A Trait subclass for colors. Color is either Blue or Yellow, with a capital B dominant gene"""

    traits = {"NN": "T1", "Nn": "T2", "nN": "T3", "nn": "T4"}
    trait_keys = list(traits.keys())

    def __init__(self, parent1_color=None, parent2_color=None):
        super().__init__(parent1_color, parent2_color, name="GenericTrait")

    def set_random_trait(self):
        self.trait = choice(self.trait_keys)
        self.trait_value = self.traits[self.trait]
