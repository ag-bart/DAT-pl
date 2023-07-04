import pandas as pd
from datpl.reader_interface import DataReader


class PandasDataReader(DataReader):
    def read_data(self, path_to_file):
        """
        Read data from the specified file using Pandas.

        Parameters:
            path_to_file (str): The path to file containing the data.

        Returns:
            List[List[str]]: The data read from the file.
        """
        if path_to_file.endswith('.xlsx'):
            df_upload = pd.read_excel(path_to_file, header=None, dtype=str)
        elif path_to_file.endswith('.csv'):
            df_upload = pd.read_csv(
                path_to_file, header=None, dtype=str, sep=';')
        else:
            raise ValueError(
                'Unsupported file type. Only XLSX and CSV files are supported.'
            )

        df_upload = df_upload.fillna(value=' ')
        data = df_upload.values.tolist()
        return data
