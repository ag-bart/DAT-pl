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
        id_column=0) -> Dict[str, List[str]]:
    """
    Read data from the specified file using Pandas.

    Parameters:
    path_to_file (str): The path to the file containing the data.
    csv_separator (str, optional): The separator for CSV files. Defaults to ';'.
    id_column (str or int, optional):
        The name or index of the column containing unique IDs. Defaults to 0.

    Returns:
    Dict[str, List[str]]: The data read from the file.
    """

    file_extension = pathlib.Path(path_to_file).suffix
    if file_extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f'Unsupported file type. Supported types are '
            f'{", ".join(SUPPORTED_FILE_TYPES)}')

    df = _read_data_from_file(path_to_file, file_extension, csv_separator)
    df = _set_unique_id_column(df, id_column)

    word_list = df.fillna('').values.tolist()
    return dict(zip(df.index.tolist(), word_list))


def _read_data_from_file(file_path, file_extension, csv_separator):
    if file_extension == '.xlsx':
        return pd.read_excel(file_path, dtype=str)
    elif file_extension == '.csv':
        return pd.read_csv(file_path, sep=csv_separator, dtype=str)
    else:
        raise ValueError(f'Unsupported file type: {file_extension}')


def _set_unique_id_column(df, id_column):
    if id_column is not None:
        if isinstance(id_column, int):
            id_column = df.columns[id_column]
        elif isinstance(id_column, str):
            if id_column not in df:
                raise ValueError(
                    f'Unique ID column "{id_column}" not found in the data.')
        else:
            raise ValueError(f'Invalid value for id_column: {id_column}')
        df.set_index(id_column, inplace=True)
    else:
        df.index = [str(uuid.uuid4()) for _ in range(len(df))]
    return df


def _generate_file_name() -> str:
    """Generate a unique file name based on the current date and time."""
    date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
    return f'dat_distances{date}.csv'


def _create_output_directory(filename: str):
    """Create the 'results' directory if it doesn't exist."""
    os.makedirs('results', exist_ok=True)
    return os.path.join('results', filename)


def _generate_column_names(minimum_words: int):
    """Generate column names based on the minimum number of words."""
    columns = ['W' + str(n) for n in range(1, minimum_words+1)]
    word_pairs_columns = [f'{c1}-{c2}' for c1, c2 in combinations(columns, 2)]
    return ['ID'] + word_pairs_columns + ['DAT']


def _save_csv_file(output_path: str, results, columns):
    """Save the computed distances to a CSV file."""
    data = [[key] + result.distances + [result.score]
            for key, result in results.items()]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_path, index=False)


def save_results(results: Dict[str, DatResult], minimum_words: int):
    """Save computed distances to a CSV file in the 'results' folder.

    Parameters:
    results (Dict[str, DatResult]): A dictionary of DatResult named tuples,
        each containing distances and scores
    minimum_words (int): The minimum number of words used to compute DAT scores.
    """

    output_path = _create_output_directory(_generate_file_name())

    column_names = _generate_column_names(minimum_words)

    _save_csv_file(output_path, results=results, columns=column_names)

    print('csv file saved in /results.')
