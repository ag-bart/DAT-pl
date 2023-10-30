import pytest
import numpy as np
from unittest.mock import Mock, patch
from datpl.processing import DatabaseManager


TEST_DB_PATH = ':memory:'


@pytest.fixture
def database_manager():
    db_manager = DatabaseManager(TEST_DB_PATH)
    yield db_manager
    db_manager.disconnect()


# Mock the sqlite3.connect method to return a mock connection
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
def test_database_manager_get_words(mock_connect, database_manager):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [('word1',), ('word2',), ('word3',)]

    # Mock the database connection and cursor
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
    # Create a mock cursor
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (np.array([1.0, 2.0, 3.0]).tobytes(),)

    # Mock the database connection and cursor
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


if __name__ == '__main__':
    pytest.main()

