import traits as t
from hashlib import md5
from datetime import datetime
import json


class Organism(object):
    def __init__(self, parent1, parent2, n_traits=2):
        self.traits = {}
        self.creation_timestamp = datetime.now().timestamp()

        # case for first generation
        if parent1 is None or parent2 is None:
            self.parent1 = None
            self.parent2 = None
            self.traits["gender"] = t.Gender()
            self.traits["color"] = t.Color()
            for i in range(n_traits - len(self.traits)):
                self.traits[f"trait{i}"] = t.GenericTrait()
            self.hash = md5(f"{self.creation_timestamp}{self.traits}".encode())
        else:  # for generation 2+
            self.parent1 = parent1
            self.parent2 = parent2
            if parent1.traits["gender"].trait == parent2.traits["gender"].trait:
                raise Exception("parents must have different genders")
            else:
                self.traits["gender"] = t.Gender(
                    parent1.traits["gender"].trait, parent2.traits["gender"].trait
                )
            self.traits["color"] = t.Color(
                parent1.traits["color"].trait, parent2.traits["color"].trait
            )
            generic_trait_dict = {
                k: v for k, v in parent1.traits.items() if "trait" in k
            }
            for k, v in generic_trait_dict.items():
                self.traits[k] = t.GenericTrait(v.trait, parent2.traits[k].trait)

            self.hash = md5(
                f"{self.creation_timestamp}{self.parent1.hash}{self.parent2.hash}{self.traits}".encode()
            )

        self.female = True if self.traits["gender"].trait == "XY" else False

    def __repr__(self):
        return f"{self.hash}|{self.parent1},{self.parent2},{self.traits}"

    def to_json(self):
        return json.dumps(self)
