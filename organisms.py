from microbit import *
import traits as t

class Organism(object):

    def __init__(self, name, parent1, parent2):
        self.name = name
        self.traits = {}

        #case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None
            self.parent2 = None
            self.traits['gender'] = t.Gender()
            self.traits['color'] = t.Color()
            self.hash = (self.name + str(self.traits))
        else: #for generation 2+
            self.parent1 = parent1.hash
            self.parent2 = parent2.hash
            if parent1.traits['gender'].trait == parent2.traits['gender'].trait:
                raise Exception('parents must have different genders')
            else:
                self.traits['gender'] = t.Gender(parent1.traits['gender'].trait, parent2.traits['gender'].trait)
            self.traits['color'] = t.Color(parent1.traits['color'].trait, parent2.traits['color'].trait)
            self.hash = (self.name + self.parent1 + self.parent2 + str(self.traits))

        self.female = True if self.traits['gender'].trait == 'XY' else False

    def __repr__(self):
        return str({'name': self.name, 'hash': self.hash, 'parent1': self.parent1, 'parent2': self.parent2,
                    'traits': self.traits})

    def update_from_repr(self, repr_string):
        org_dict = eval(repr_string)
        self.name = org_dict['name']
        self.parent1 = org_dict['parent1']
        self.parent2 = org_dict['parent2']
        self.traits['color'].trait = org_dict['traits']['color']['trait']
        self.traits['color'].trait_value = org_dict['traits']['color']['trait_value']
        self.traits['gender'].trait = org_dict['traits']['gender']['trait']
        self.traits['gender'].trait_value = org_dict['traits']['gender']['trait_value']
