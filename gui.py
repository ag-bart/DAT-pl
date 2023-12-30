"""Simple GUI for calculating DAT scores."""
import tkinter as tk
from tkinter import filedialog
from datpl.processing import DatabaseManager, DataProcessor
from datpl.data_io import read_data, save_results
from datpl.analysis import DatComputer


def calculate_dat(data_file, database_path):
    """Basic DAT calculation for the GUI

    Args:
        data_file (str): File with words to be scored.
        database_path (str): Path to vectors.db database file.
    """
    # initialize objects for data processing
    dataset = read_data(data_file, id_column=0)
    db_manager = DatabaseManager(database_path)
    data_cleaner = DataProcessor(words=db_manager.get_words())

    # validate dataset against the database
    processed_dataset = data_cleaner.process_dataset(dataset)

    # assign to a variable the final dataset (containing only correct words)
    valid_responses = data_cleaner.extract_valid_words(processed_dataset)

    # initialize the main class instance for scoring DAT
    model = DatComputer(db_manager)

    # compute the DAT score
    results = model.dataset_compute_dat_score(valid_responses)
    db_manager.disconnect()

    # obtain a csv file with the final DAT score and distances between word pairs
    save_results(results, minimum_words=model.minimum_words)


window = tk.Tk()
window.title("Calculate DAT")


def run_calculate_dat():
    """Run the DAT calculation and print a message."""
    data_file = data_file_path.get()
    database_path = database_file_path.get()

    calculate_dat(data_file, database_path)

    tk.messagebox.showinfo(
        "Calculation Complete", "DAT calculation completed successfully!"
    )


def select_data_file():
    """Open a file dialog to select the data file."""
    file_path = filedialog.askopenfilename()
    data_file_path.delete(0, tk.END)
    data_file_path.insert(tk.END, file_path)


def select_database_path():
    """Open a file dialog to select the vectors.db database file."""
    file_path = filedialog.askopenfilename()
    database_file_path.delete(0, tk.END)
    database_file_path.insert(tk.END, file_path)


data_file_path_label = tk.Label(window, text="Data File:")
data_file_path_label.pack()

data_file_path = tk.Entry(window)
data_file_path.pack()

data_file_button = tk.Button(window, text="Select Data File", command=select_data_file)
data_file_button.pack()

database_file_path_label = tk.Label(window, text="Database File:")
database_file_path_label.pack()

database_file_path = tk.Entry(window)
database_file_path.pack()

database_button = tk.Button(
    window, text="Select Database File", command=select_database_path
)
database_button.pack()

calculate_button = tk.Button(window, text="Calculate DAT", command=run_calculate_dat)
calculate_button.pack()

window.mainloop()
