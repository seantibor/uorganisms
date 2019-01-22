from organisms import Organism
from random import normalvariate, shuffle

overall_stats = {}


def create_generation(
        current_generation,
        generation_number,
        population_cap=2000,
        family_size=2.1,
        family_stdev=0.9,
        current_females=None,
        current_males=None,
):
    global overall_stats

    # initialize lists to contain next generation of organisms
    next_generation = []
    next_females = []
    next_males = []
    if current_females is None:
        current_females = [org for org in current_generation if org.female]
    if current_males is None:
        current_males = [org for org in current_generation if not org.female]
    # initialize current generation's statistics tracker
    generation_stats = {
        "gen": generation_number,
        "total_pop": 0,
        "female": 0,
        "male": 0,
        "blue": 0,
        "yellow": 0,
        "BB": 0,
        "Bb": 0,
        "bb": 0,
    }

    # loop through male list to reproduce
    shuffle(current_females)
    shuffle(current_males)
    for male in current_males:
        # reproduce if we have females available and haven't reached the population cap
        if len(current_females) > 0 and len(next_generation) < population_cap:
            # get a female Organism for reproduction. candidate is removed from reproduction pool
            female = current_females.pop()
            # each pairing results in a family of offspring to maintain or grow population
            for children in range(round(normalvariate(family_size, family_stdev))):
                # create a child
                child = Organism(male, female)
                # increase total population
                generation_stats["total_pop"] += 1
                # increment counters for each trait value, e.g. Male or Blue
                for key, value in child.traits.items():
                    if "trait" not in key:
                        generation_stats[value.trait_value.lower()] += 1
                        # track color gene pairings separately
                        if key == "color":
                            generation_stats[value.trait] += 1
                # add child to appropriate lists for next generation
                next_generation.append(child)
                if child.female:
                    next_females.append(child)
                else:
                    next_males.append(child)

    # once all children have been created, advance to the next generation
    current_generation = next_generation
    current_females = next_females
    current_males = next_males

    add_generation_stats(generation_stats)

    return current_generation, current_females, current_males


def create_generation_stats(current_generation, current_females, current_males):
    global overall_stats
    # initialize overall_stats dictionary to track current generation statistics
    overall_stats = {
        "gen": [1],
        "total_pop": [len(current_generation)],
        "female": [len(current_females)],
        "male": [len(current_males)],
    }
    overall_stats["blue"] = [
        sum(org.traits["color"].trait_value == "Blue" for org in current_generation)
    ]
    overall_stats["yellow"] = [
        sum(org.traits["color"].trait_value == "Yellow" for org in current_generation)
    ]
    overall_stats["BB"] = [
        sum(org.traits["color"].trait == "BB" for org in current_generation)
    ]
    overall_stats["Bb"] = [
        sum(org.traits["color"].trait == "Bb" for org in current_generation)
    ]
    overall_stats["bb"] = [
        sum(org.traits["color"].trait == "bb" for org in current_generation)
    ]


def add_generation_stats(gen_stats):
    global overall_stats
    if overall_stats is None:
        overall_stats = []
    # add all stats for the current generation to the overall stats list
    for key, value in gen_stats.items():
        overall_stats[key].append(value)


def get_overall_stats():
    return overall_stats


def test_run(
        initial_pop=1000, n_generations=500, pop_cap=2000, f_size=2.1, f_stdev=0.9
):
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
    current_generation = [Organism(None, None, n_traits=5) for i in range(initial_pop)]
    # current_generation = [org for org in current_generation if org.traits['color'].trait_value == "Blue"]

    # create gender lists to support reproduction
    current_females = [org for org in current_generation if org.female]
    current_males = [org for org in current_generation if not org.female]

    create_generation_stats(current_generation, current_females, current_males)

    # show first generation statistics
    print(
        "{} male and {} female organisms in first generation".format(
            len(current_males), len(current_females)
        )
    )

    # for organism in current_generation:
    #    print('The organism named {} is {} with {} color.'.format(organism.name, organism.traits['gender'], organism.traits['color']))

    # generation simulation loop
    for i in range(2, n_generations + 1):

        # initialize current generation's statistics tracker
        generation_stats = {
            "gen": i,
            "total_pop": 0,
            "female": 0,
            "male": 0,
            "blue": 0,
            "yellow": 0,
            "BB": 0,
            "Bb": 0,
            "bb": 0,
        }

        # once all children have been created, advance to the next generation
        current_generation, current_females, current_males = create_generation(
            current_generation,
            i,
            current_females=current_females,
            current_males=current_males,
            population_cap=pop_cap,
            family_size=f_size,
            family_stdev=f_stdev,
        )

        # print some stats on current generation while simulation is running
        print(
            "Gen {}: {} male and {} female organisms".format(
                i, len(current_males), len(current_females)
            )
        )
        if len(current_generation) == 0:
            break
