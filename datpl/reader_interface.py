from abc import ABC, abstractmethod


class DataReader(ABC):
    @abstractmethod
    def read_data(self, path_to_file):
        """method to be implemented by subclasses to read data from a file."""
