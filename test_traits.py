from organisms import Organism
from random import normalvariate, sample
import pandas as pd
import matplotlib.pyplot as plt

INITIAL_POP = 1000
GENERATIONS = 500
POPULATION_CAP = 2000
FAMILY_SIZE = 2.1
FAMILY_STDEV = 0.9

def main():
    """ Test function for Organisms and Traits classes

        Creates an initial population of Organisms, simulates reproduction up to a
        population cap over generations. Any remaining organisms left over when population cap
        is reached are culled.

        Constants:
            INITIAL_POP - the number of Organisms in the first generation
            GENERATIONS - the number of generations to simulate
            POPULATION_CAP - the maximum number of Organisms in any generation

    """
    # create a list of organisms to test in current generation
    current_generation = [Organism('Bob{}'.format(i), None, None) for i in range(INITIAL_POP)]
    current_generation = [org for org in current_generation if org.traits['color'].trait_value == "Blue"]

    # create gender lists to support reproduction
    current_females = set([org for org in current_generation if org.female])
    current_males = set([org for org in current_generation if not org.female])

    # initialize overall_stats dictionary to track current generation statistics
    overall_stats = {'gen': [1], 'total_pop': [len(current_generation)], 'female': [len(current_females)],
                     'male': [len(current_males)]}
    overall_stats['blue'] = [sum(org.traits['color'].trait_value == 'Blue' for org in current_generation)]
    overall_stats['yellow'] = [sum(org.traits['color'].trait_value == 'Yellow' for org in current_generation)]
    overall_stats['BB'] = [sum(org.traits['color'].trait == 'BB' for org in current_generation)]
    overall_stats['Bb'] = [sum(org.traits['color'].trait == 'Bb' for org in current_generation)]
    overall_stats['bb'] = [sum(org.traits['color'].trait == 'bb' for org in current_generation)]

    # show first generation statistics
    print('{} male and {} female organisms in first generation'.format(len(current_males), len(current_females)))

    # for organism in current_generation:
    #    print('The organism named {} is {} with {} color.'.format(organism.name, organism.traits['gender'], organism.traits['color']))

    # generation simulation loop
    for i in range(2, GENERATIONS + 1):

        # initialize lists to contain next generation of organisms
        next_generation = set()
        next_females = set()
        next_males = set()
        # initialize current generation's statistics tracker
        generation_stats = {'gen': i, 'total_pop': 0, "female": 0,
                            'male': 0, 'blue': 0, 'yellow': 0, 'BB': 0, 'Bb': 0, 'bb': 0}

        # loop through male list to reproduce
        for male in current_males:
            # reproduce if we have females available and haven't reached the population cap
            if len(current_females) > 0 and len(next_generation) < POPULATION_CAP:
                # get a female Organism for reproduction. candidate is removed from reproduction pool
                female = sample(current_females, 1)[0]
                # each pairing results in a family of offspring to maintain or grow population
                for children in range(round(normalvariate(FAMILY_SIZE, FAMILY_STDEV))):
                    # create a child
                    child = Organism('bob',male, female)
                    # increase total population
                    generation_stats['total_pop'] += 1
                    # increment counters for each trait value, e.g. Male or Blue
                    for key, value in child.traits.items():
                        generation_stats[value.trait_value.lower()] += 1
                        # track color gene pairings separately
                        if key == 'color':
                            generation_stats[value.trait] += 1
                    # add child to appropriate lists for next generation
                    next_generation.add(child)
                    if child.female:
                        next_females.add(child)
                    else:
                        next_males.add(child)

        # once all children have been created, advance to the next generation
        current_generation = next_generation
        current_females = next_females
        current_males = next_males

        # add all stats for the current generation to the overall stats list
        for key, value in generation_stats.items():
            overall_stats[key].append(value)

        # print some stats on current generation while simulation is running
        print('Gen {}: {} male and {} female organisms'.format(i, len(current_males), len(current_females)))

    # create a pandas dataframe from the overall statistics
    df = pd.DataFrame.from_dict(overall_stats)
    df.index = df.loc[:,'gen']

    # plot the color genes
    print(df.describe())
    df.plot(y=['total_pop', 'BB', 'Bb', 'bb'])
    plt.show()
    print(df.iloc[0])

    # plot the color trait percentages by generation
    df['BluePct'] = df['blue'] / df['total_pop']
    df['YellowPct'] = df['yellow'] / df['total_pop']

    df.plot(y=['BluePct', 'YellowPct'])
    plt.show()

    print(repr(sample(current_generation, 1)[0]))
if __name__ == '__main__':
    main()
