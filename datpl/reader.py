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
