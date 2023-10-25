import os
import time
import pathlib
import uuid
from itertools import combinations
from typing import List, Dict
import pandas as pd

from .analysis import DatResult


SUPPORTED_FILE_TYPES = ['.xlsx', '.csv']


def read_data(
        path_to_file,
        csv_separator=';',
        unique_id_column=0) -> Dict[str, List[str]]:
    """
    Read data from the specified file using Pandas.

    Parameters:
    path_to_file (str): The path to the file containing the data.
    csv_separator (str, optional): The separator for CSV files. Defaults to ';'.
    unique_id_column (str or int, optional):
        The name or index of the column containing unique IDs. Defaults to 0.

    Returns:
    Dict[str, List[str]]: The data read from the file.
    """

    file_extension = pathlib.Path(path_to_file).suffix
    if file_extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f'Unsupported file type. Supported types are'
            f' {", ".join(SUPPORTED_FILE_TYPES)}')

    if file_extension == '.xlsx':
        df = pd.read_excel(path_to_file, dtype=str)
    elif file_extension == '.csv':
        df = pd.read_csv(path_to_file, sep=csv_separator, dtype=str)

    if isinstance(unique_id_column, int):
        unique_id_column = df.columns[unique_id_column]

    if isinstance(unique_id_column, str):
        if unique_id_column not in df:
            raise ValueError(
                f'Unique ID column "{unique_id_column}" not found in the data.')
        df.set_index(unique_id_column, inplace=True)
    else:
        # Generate unique IDs if no column specified
        df.index = [str(uuid.uuid4()) for _ in range(len(df))]

    word_list = df.fillna('').values.tolist()
    return dict(zip(df.index.tolist(), word_list))


def save_results(results: Dict[str, DatResult], minimum_words: int):
    """Save computed distances to a CSV file in the 'results' folder.

    Parameters:
    results (Dict[str, DatResult]): A dictionary of DatResult named tuples,
        each containing distances and scores
    minimum_words (int): The minimum number of words used to compute DAT scores.
    """

    date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
    file_name = f'dat_distances{date}.csv'
    output_path = os.path.join('results', file_name)

    if not os.path.exists(output_path):
        os.makedirs('results', exist_ok=True)

    columns = ['W' + str(n) for n in range(1, minimum_words+1)]
    column_names = [f'{c1}-{c2}' for c1, c2 in combinations(columns, 2)]

    data = [result.distances + [result.score] for result in results.values()]

    df = pd.DataFrame(data, columns=column_names + ['DAT'])
    df.index = results.keys()
    df.to_csv(output_path)
    print('csv file saved in /results.')
