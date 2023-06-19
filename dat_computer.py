import itertools
import time
import pandas as pd
from dat import Model
from decorators import dict_decorator, round_output


class DatComputer(Model):
    def __init__(self, data, **kwargs):
        super(DatComputer, self).__init__(**kwargs)
        self.data = data
        self.dat_values = []
        self.dat_distances = []

    @dict_decorator
    def inv_words(self):
        """Return a dictionary of words not found in model.

        Returns
        -------
        key : int
            index of participant's answer increased by 1 to reflect id in file
        value : list[str]
            list of incorrect words
        """

        inv_dict = {}
        for answer in self.data:
            invalid_list = [word for words in answer if (word := self.get_invalid(words)) is not None]
            if len(invalid_list) > 0:
                inv_dict[(self.data.index(answer) + 1)] = invalid_list
        return inv_dict

    @round_output
    def compute_dat(self):
        """return mean distances multiplied by 100 for each participant"""

        self.dat_values = [((sum(distances) / len(distances)) * 100)
                           if len(distances) != 0 else None
                           for distances in self.distances_by_pairs()]
        return self.dat_values

    def distances_by_pairs(self):
        self.dat_distances = [self.dat(answer) for answer in self.data]
        return self.dat_distances

    def save_distances(self):
        columns = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']
        column_names = [f'{c1}-{c2}'
                        for c1, c2 in itertools.combinations(columns, 2)]

        date = time.strftime("%Y-%b-%d__%H_%M_%S", time.localtime())
        df = pd.DataFrame(self.dat_distances, columns=column_names)
        df['DAT'] = self.dat_values
        df.to_csv(f'dat_distances{date}.csv')
