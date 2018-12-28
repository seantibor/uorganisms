import pip
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 
from random import choice
from collections import Counter

from random import choice
from collections import Counter

trait_perms = ('BB', 'bb','Bb','bB')
test_results = []


def select_trait(parent1, parent2):
    """return a pair of genes based on random selection
    parent parameters: strings of 2 character genes from first parent"""
    return choice([x + y for x in parent1 for y in parent2])

#in return choice are you only selecting the x from parent 1 and the y from parent2? or are they a random selection from each trait_perm?


def main():
    parent1 = choice(trait_perms)
    for _ in range(1000):
        parent2 = choice(trait_perms)
        child = select_trait(parent1,parent2)
        test_results.append(child)
        parent1 = child

    trait_counter = Counter(test_results)
    for perm in trait_perms:
        print('{} trait: {} outcomes'.format(perm, trait_counter[perm]))


if __name__ == '__main__':
    main()
