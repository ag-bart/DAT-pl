import os
import time
from itertools import combinations
from typing import List
import pandas as pd

from .analysis import DatResult



def read_data(path_to_file):
    """
    Read data from the specified file using Pandas.

    Parameters:
        path_to_file (str): The path to file containing the data.

    Returns:
        List[List[str]]: The data read from the file.
    """
    if path_to_file.endswith('.xlsx'):
        df = pd.read_excel(path_to_file, header=None, dtype=str)
    elif path_to_file.endswith('.csv'):
        df = pd.read_csv(path_to_file, header=None, dtype=str, sep=';')
    else:
        raise ValueError(
            'Unsupported file type. Only XLSX and CSV files are supported.')

    data = df.fillna(value=' ').values.tolist()
    return data


def save_results(results: List[DatResult], minimum_words: int):
    """Save computed distances to a CSV file in the 'results' folder.

    Parameters:
        results (List[DatResult]):
            A list of DatResult named tuples, each containing distances
            and scores for a set of words.
        minimum_words (int):
            The minimum number of words used to compute DAT scores.
    """

    date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
    file_name = f'dat_distances{date}.csv'
    output_path = os.path.join('results', file_name)

    if not os.path.exists(output_path):
        os.makedirs('results', exist_ok=True)

    columns = ['W' + str(n) for n in range(1, minimum_words+1)]
    column_names = [f'{c1}-{c2}' for c1, c2 in combinations(columns, 2)]

    data = [result.distances + [result.score] for result in results]
    df = pd.DataFrame(data, columns=column_names + ['DAT'])

    df.to_csv(output_path)
    print('csv file saved in /results.')
