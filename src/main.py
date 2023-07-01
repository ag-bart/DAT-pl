import os
from data.create_database import read_data
from src.distance_analyzer import DistanceAnalyzer
from src.database_manager import DatabaseManager
from src.word_cleaner import WordCleaner
from src.dat_computer import DatComputer


if __name__ == '__main__':

    filename = 'dat-data.xlsx'
    # TODO: run create_database.py if vectors.db not found
    database_path = os.path.join('..', 'data', 'vectors.db')
    file_path = os.path.join('..', 'data', filename)

    dat_data = read_data(file_path)
    db_manager = DatabaseManager(database_path)
    data_cleaner = WordCleaner(db_manager)
    data_analyzer = DistanceAnalyzer(db_manager, data_cleaner)
    dataset_analyzer = DatComputer(data_analyzer, data_cleaner, data=dat_data)

    db_manager.disconnect()
