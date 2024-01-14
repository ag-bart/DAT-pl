import os
import tempfile
import shutil

import pytest
import pandas as pd

from datpl.analysis import DatResult
from datpl.data_io import (
    read_data,
    save_results,
    _save_csv_file,
    _generate_column_names,
    _generate_file_name,
    _create_output_directory,
    _read_data_from_file,
    _set_unique_id_column
)


test_data = {
    'ID': ['a1', 'a2', 'a3'],
    'W1': ['word1', 'word2', 'word3'],
    'W2': ['word4', 'word5', 'word6'],
}


@pytest.fixture
def sample_data_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'sample_data.csv')
        df = pd.DataFrame(test_data)
        df.to_csv(file_path, index=False)
        yield file_path


def test_read_data(sample_data_csv):
    data = read_data(sample_data_csv, csv_separator=',')
    expected_data = {
        'a1': ['word1', 'word4'],
        'a2': ['word2', 'word5'],
        'a3': ['word3', 'word6'],
    }
    assert data == expected_data


def test_read_xlsx_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'sample_data.xlsx')
        df = pd.DataFrame(test_data)
        df.to_excel(file_path, index=False)
        data = read_data(file_path)
        expected_data = {
            'a1': ['word1', 'word4'],
            'a2': ['word2', 'word5'],
            'a3': ['word3', 'word6'],
        }
        assert data == expected_data


def test_read_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file type"):
        read_data('unsupported_file.txt')


def test_read_data_from_file(sample_data_csv):
    data = _read_data_from_file(sample_data_csv, '.csv', ',')
    expected_data = pd.DataFrame(test_data)
    pd.testing.assert_frame_equal(data, expected_data)


def test_invalid_file_type():
    with pytest.raises(ValueError):
        _read_data_from_file('invalid_file.pdf', '.pdf')


def test_set_unique_id_column():
    test_df = pd.DataFrame({'ID': ['a1', 'a2', 'a3'], 'A': [10, 20, 30]})
    df = _set_unique_id_column(test_df, 'ID')
    assert df.index.name == 'ID'


def test_set_unique_id_column_with_invalid_string_column():
    with pytest.raises(ValueError, match='Unique ID column "ID" not found'):
        test_df = pd.DataFrame({'A': [10, 20, 30]})
        _set_unique_id_column(test_df, 'ID')


def test_set_unique_id_column_with_invalid_type_column():
    test_df = pd.DataFrame({'A': [10, 20, 30]})
    with pytest.raises(ValueError, match="Invalid value for id_column"):
        _set_unique_id_column(test_df, 0.5)


def test_set_unique_id_column_with_none_id_column():
    test_df = pd.DataFrame({'A': [10, 20, 30]})
    modified_df = _set_unique_id_column(test_df, None)
    for index in modified_df.index:
        assert isinstance(index, str)
        assert len(index) == 36  # UUID string length


def test_generate_file_name():
    file_name = _generate_file_name()
    assert file_name.startswith('dat_distances20')
    assert file_name.endswith('.csv')


def test_generate_column_names():
    columns = _generate_column_names(3)
    expected_columns = ['ID', 'W1-W2', 'W1-W3', 'W2-W3', 'DAT']
    assert columns == expected_columns


def test_create_output_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = _create_output_directory(tmp_dir)
        assert os.path.exists(output_dir)
        assert os.path.isdir(output_dir)


def test_save_csv_file():
    data = {
        'a1': DatResult([0.5, 0.6, 0.7], 0.8),
        'a2': DatResult([0.4, 0.5, 0.6], 0.7),
    }
    columns = ['ID', 'W1-W2', 'W1-W3', 'W2-W3', 'DAT']
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, 'output.csv')
        _save_csv_file(output_path, data, columns)

        df = pd.read_csv(output_path)
        expected_data = {
            'ID': ['a1', 'a2'],
            'W1-W2': [0.5, 0.4],
            'W1-W3': [0.6, 0.5],
            'W2-W3': [0.7, 0.6],
            'DAT': [0.8, 0.7],
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)


# create and clean up the 'results' folder
@pytest.fixture(scope="function")
def results_folder():
    os.makedirs('results', exist_ok=True)

    yield

    shutil.rmtree('results', ignore_errors=True)


def test_save_results(capsys, results_folder):
    data = {
        '1': DatResult([0.5, 0.6, 0.7], 0.8),
        '2': DatResult([0.4, 0.5, 0.6], 0.7),
    }

    output_path = save_results(data, 3)
    assert os.path.exists(output_path)
    assert os.path.isfile(output_path)

    captured = capsys.readouterr()

    expected_message = f'CSV file saved in {output_path}.\n'
    assert captured.out == expected_message
