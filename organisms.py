from traits import Gender, Color
from hashlib import md5

class Organism(object):

    def __init__(self, name, parent1, parent2):
        self.name = name
        self.traits = {}

        #case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None
            self.parent2 = None
            self.traits['gender'] = Gender()
            self.traits['color'] = Color()
            self.hash = md5(self.name.encode() + str(self.traits).encode()).digest()
        else: #for generation 2+
            self.parent1 = parent1.hash
            self.parent2 = parent2.hash
            if parent1.traits['gender'].trait == parent2.traits['gender'].trait:
                raise Exception('parents must have different genders')
            else:
                self.traits['gender'] = Gender(parent1.traits['gender'].trait, parent2.traits['gender'].trait)
            self.traits['color'] = Color(parent1.traits['color'].trait, parent2.traits['color'].trait)
            self.hash = md5(self.name.encode() + self.parent1 + self.parent2 + str(self.traits).encode()).digest()

        self.female = True if self.traits['gender'].trait == 'XY' else False

    def __repr__(self):
        return str({'name': self.name, 'hash': self.hash, 'traits': self.traits})
