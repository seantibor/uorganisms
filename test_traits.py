import generations
from organisms import Organism
import pandas as pd
import matplotlib.pyplot as plt

INITIAL_POP = 1000
GENERATIONS = 500
POPULATION_CAP = 2000
FAMILY_SIZE = 2.1
FAMILY_STDEV = 0.9


def main(plot_data=True):
    generations.test_run(
        INITIAL_POP, GENERATIONS, POPULATION_CAP, FAMILY_SIZE, FAMILY_STDEV
    )

    if plot_data:
        overall_stats = generations.get_overall_stats()
        # create a pandas dataframe from the overall statistics
        df = pd.DataFrame.from_dict(overall_stats)
        df.index = df.loc[:, "gen"]

        # plot the color genes
        print(df.describe())
        df.plot(y=["total_pop", "BB", "Bb", "bb"])
        plt.show()
        print(df.iloc[0])

        # plot the color trait percentages by generation
        df["BluePct"] = df["blue"] / df["total_pop"]
        df["YellowPct"] = df["yellow"] / df["total_pop"]

        df.plot(y=["BluePct", "YellowPct"])
        plt.show()


if __name__ == "__main__":
    main()
