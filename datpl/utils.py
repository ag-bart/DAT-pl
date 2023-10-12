import os
import time
from itertools import combinations
import pandas as pd


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


def save_results(results, words_number):
    """Save computed distances to a CSV file in the 'results' folder."""

    date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
    file_name = f'dat_distances{date}.csv'
    output_path = os.path.join('results', file_name)

    if not os.path.exists(output_path):
        os.makedirs('results', exist_ok=True)

    columns = ['W' + str(n) for n in range(1, words_number+1)]
    column_names = [f'{c1}-{c2}' for c1, c2 in combinations(columns, 2)]

    df = pd.DataFrame(results[0], columns=column_names)
    df['DAT'] = results[1]

    df.to_csv(output_path)
    print('csv file saved in /results.')
