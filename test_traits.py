from organisms import Organism
from random import normalvariate
import pandas as pd
import matplotlib.pyplot as plt

def main():
    test_organisms = [Organism('Bob{}'.format(i), None, None) for i in range(1000)]
    female_organisms = [org for org in test_organisms if org.traits['gender'].trait == 'XX']
    male_organisms = [org for org in test_organisms if org not in female_organisms]
    blues = sum(org.traits['color'].trait_value == 'Blue' for org in test_organisms)
    yellows = sum(org.traits['color'].trait_value == 'Yellow' for org in test_organisms)

    overall_stats = {'gen': [1], 'total_pop': [len(test_organisms)], 'female': [len(female_organisms)],
                     'male': [len(male_organisms)], 'blue': [blues], 'yellow': [yellows]}

    print('{} male and {} female organisms in first generation'.format(len(male_organisms), len(female_organisms)))

    #for organism in test_organisms:
    #    print('The organism named {} is {} with {} color.'.format(organism.name, organism.traits['gender'], organism.traits['color']))

    for i in range(2, 501):

        next_generation = []
        next_females = []
        next_males = []
        generation_stats = {'gen': i, 'total_pop': 0, "female": 0,
                            'male': 0, 'blue': 0, 'yellow': 0}
        for male in male_organisms:
            if len(female_organisms) > 0 and len(next_generation) < 5001:
                female = female_organisms.pop()
                for children in range(round(normalvariate(2.1,.9))):
                    child = Organism('bob',male, female)
                    generation_stats['total_pop'] += 1
                    for key, value in child.traits.items():
                        generation_stats[value.trait_value.lower()] += 1
                    next_generation.append(child)
                    if child.traits['gender'].trait_value == 'Female':
                        next_females.append(child)
                    else:
                        next_males.append(child)

        test_organisms = next_generation
        for key, value in generation_stats.items():
            overall_stats[key].append(value)

        female_organisms = next_females
        male_organisms = next_males
        print('Gen {}: {} male and {} female organisms'.format(i, len(male_organisms), len(female_organisms)))

    df = pd.DataFrame.from_dict(overall_stats)
    df.index = df.loc[:,'gen']

    print(df.describe())
    df.plot(y = ['total_pop', 'male','female','blue','yellow'])
    plt.show()


if __name__ == '__main__':
    main()
