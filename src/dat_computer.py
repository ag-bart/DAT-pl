import os
import time
import itertools
from typing import Dict
import pandas as pd
from src.decorators import format_dict_output, round_output


class DatComputer:
    def __init__(self, distance_analyzer, word_cleaner, data):
        self.analyzer = distance_analyzer
        self.cleaner = word_cleaner
        self.data = data

        self.invalid_dict: Dict[str] = {}
        self.dat_distances = None
        self.dat_values = None

    @format_dict_output
    def invalid_words(self):
        invalid_dict = {
            i: [self.cleaner.validate(word)[1] for word in answer if
                self.cleaner.validate(word)[1] is not None]
            for i, answer in enumerate(self.data)
        }

        self.invalid_dict = {k: v for k, v in invalid_dict.items() if v}
        return self.invalid_dict

    @round_output
    def compute_dat(self):
        """return mean distances multiplied by 100 for each participant"""
        dat_values = [((sum(distances) / len(distances)) * 100)
                      if len(distances) != 0 else None
                      for distances in self.distances_by_pairs()]

        self.dat_values = dat_values
        return self.dat_values

    def distances_by_pairs(self):
        dat_distances = [self.analyzer.dat(answer) for answer in self.data]
        self.dat_distances = dat_distances
        return self.dat_distances

    def save_distances(self):
        columns = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']
        column_names = [f'{c1}-{c2}'
                        for c1, c2 in itertools.combinations(columns, 2)]

        date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
        file_name = f'dat_distances{date}.csv'
        # TODO: check if path exists
        output_path = os.path.join('results', file_name)

        if not os.path.exists(output_path):
            os.makedirs('results', exist_ok=True)

        if not self.dat_distances:
            self.compute_dat()

        df = pd.DataFrame(self.dat_distances, columns=column_names)
        df['DAT'] = self.dat_values
        df.to_csv(output_path)
        print('csv file saved in /results.')
