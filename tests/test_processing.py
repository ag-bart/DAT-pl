import sqlite3
from unittest.mock import Mock, patch

import pytest
import numpy as np

from datpl.processing import DataProcessor, DatabaseManager


TEST_DB_PATH = ':memory:'


@pytest.fixture
def database_manager():
    db_manager = DatabaseManager(TEST_DB_PATH)
    yield db_manager
    db_manager.disconnect()


@patch('datpl.processing.sqlite3.connect')
def test_database_manager_connect(mock_connect, database_manager):
    database_manager.connect()
    assert database_manager.connection is not None
    mock_connect.assert_called_with(TEST_DB_PATH)


def test_database_manager_disconnect(database_manager):
    database_manager.connect()
    database_manager.disconnect()
    assert database_manager.connection is None


@patch('datpl.processing.sqlite3.connect')
def test_database_manager_connect_with_error(mock_connect, database_manager):
    mock_connect.side_effect = sqlite3.Error("Simulated database error")

    with pytest.raises(ConnectionError,
                       match="Error connecting to the database: "
                             "Simulated database error"):
        database_manager.connect()

    assert database_manager.connection is None


@patch('datpl.processing.sqlite3.connect')
def test_database_manager_get_words(mock_connect, database_manager):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [('word1',), ('word2',), ('word3',)]

    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    words = database_manager.get_words()

    assert isinstance(words, list)
    assert words == ['word1', 'word2', 'word3']
    mock_connect.assert_called_with(TEST_DB_PATH)
    mock_cursor.execute.assert_called_with('SELECT word FROM vectors')
    mock_connection.close.assert_called_once()


@patch('datpl.processing.sqlite3.connect')
def test_database_manager_get_word_vector(mock_connect, database_manager):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (np.array([1.0, 2.0, 3.0]).tobytes(),)

    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    word = "test_word"
    vector = database_manager.get_word_vector(word)

    assert isinstance(vector, np.ndarray)
    assert np.array_equal(vector, np.array([1.0, 2.0, 3.0]))
    mock_connect.assert_called_with(TEST_DB_PATH)
    mock_cursor.execute.assert_called_with(
        'SELECT vector FROM vectors WHERE word=?', (word,))


@patch('datpl.processing.sqlite3.connect')
def test_database_manager_get_non_existing_word_vector(
        mock_connect, database_manager):

    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = None

    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    non_existing_word = "non_existing_word"
    vector = database_manager.get_word_vector(non_existing_word)

    assert vector is None
    mock_connect.assert_called_with(TEST_DB_PATH)
    mock_cursor.execute.assert_called_with(
        'SELECT vector FROM vectors WHERE word=?', (non_existing_word,))


valid_words = ["jabłko", "banan", "wiśnia", "gruszka"]


@pytest.fixture
def data_processor_instance():
    return DataProcessor(valid_words)


def test_clean():
    assert DataProcessor.clean("Jabłko") == "jabłko"
    assert DataProcessor.clean("1@3") == ""
    assert DataProcessor.clean("  word  ") == "word"


def test_validate(data_processor_instance):
    assert data_processor_instance.validate("jabłko") == ("jabłko", "")
    assert data_processor_instance.validate("wiśnia") == ("wiśnia", "")
    assert data_processor_instance.validate("pear") == ("", "pear")


def test_validate_non_string_input(data_processor_instance):
    with pytest.raises(ValueError):
        data_processor_instance.validate(123)


def test_process_words(data_processor_instance):
    words = ["jabłko", "wiśnia", "banan", "gruszka", "pear", "1@3"]
    result = data_processor_instance.process_words(words)
    assert result["valid_words"] == ["jabłko", "wiśnia", "banan", "gruszka"]
    assert result["invalid_words"] == ["pear"]


def test_process_dataset(data_processor_instance):
    dataset = {
        "participant1": ["jabłko", "banan", "wiśnia"],
        "participant2": ["gruszka", "pear", "1@3"],
    }
    result = data_processor_instance.process_dataset(dataset)
    assert result["participant1"]["valid_words"] == ["jabłko", "banan",
                                                     "wiśnia"]
    assert result["participant1"]["invalid_words"] == []
    assert result["participant2"]["valid_words"] == ["gruszka"]
    assert result["participant2"]["invalid_words"] == ["pear"]


def test_extract_valid_words():
    dataset = {
        "participant1": {
            "valid_words": ["jabłko", "banan", "wiśnia"], "invalid_words": []
        },
        "participant2": {
            "valid_words": ["gruszka"], "invalid_words": ["pear"]
        },
    }
    result = DataProcessor.extract_valid_words(dataset)
    assert result["participant1"] == ["jabłko", "banan", "wiśnia"]
    assert result["participant2"] == ["gruszka"]


