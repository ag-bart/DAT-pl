"""Simple GUI for calculating DAT scores."""

import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datpl.processing import DatabaseManager, DataProcessor
from datpl.data_io import read_data, save_results
from datpl.analysis import DatComputer
from datpl.database.create_database import create_vectors_database


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
    if mode.get() == 1:
        if data_file.endswith(".csv"):
            df = pd.read_csv(data_file)
        elif data_file.endswith(".xlsx"):
            df = pd.read_excel(data_file)
        else:
            raise ValueError("Invalid file format")
        df.drop(df.columns[0], axis=1, inplace=True)
        with open("words_temp.txt", "w", encoding="UTF-8") as file:
            for col in df.columns:
                file.write("\n".join(df[col].dropna()) + "\n")
        create_vectors_database("db_temp.db", "words_temp.txt", model_file_path.get())
        database_path = "db_temp.db"
    elif mode.get() == 2:
        database_path = database_file_path.get()

    calculate_dat(data_file, database_path)

    if mode.get() == 1:
        os.remove("words_temp.txt")
        os.remove("db_temp.db")

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


def select_model_path():
    """Open a file dialog to select the GloVe model file."""
    file_path = filedialog.askopenfilename()
    model_file_path.delete(0, tk.END)
    model_file_path.insert(tk.END, file_path)


data_file_path_label = tk.Label(window, text="Data file:")
data_file_path_label.pack()

data_file_path = tk.Entry(window)
data_file_path.pack()

data_file_button = tk.Button(window, text="Select data file", command=select_data_file)
data_file_button.pack()


def update_mode(*args):
    if mode.get() == 1:
        calculate_button.pack_forget()
        model_file_path_label.pack()
        model_file_path.pack()
        model_button.pack()
        calculate_button.pack()

        database_file_path_label.pack_forget()
        database_file_path.pack_forget()
        database_button.pack_forget()
    elif mode.get() == 2:
        calculate_button.pack_forget()
        database_file_path_label.pack()
        database_file_path.pack()
        database_button.pack()
        calculate_button.pack()

        model_file_path_label.pack_forget()
        model_file_path.pack_forget()
        model_button.pack_forget()


mode_selector_label = tk.Label(window, text="Mode:")
mode_selector_label.pack()

mode = tk.IntVar()
mode.trace_add("write", update_mode)
mode_new_database = tk.Radiobutton(
    window, variable=mode, text="Create a new database", value=1
)
mode_existing_database = tk.Radiobutton(
    window, variable=mode, text="Use an existing database", value=2
)
mode_new_database.pack()
mode_existing_database.pack()

model_file_path_label = tk.Label(window, text="GloVe model file:")
model_file_path = tk.Entry(window)
model_button = tk.Button(
    window, text="Select GloVe model file", command=select_model_path
)

database_file_path_label = tk.Label(window, text="Database file:")
database_file_path = tk.Entry(window)
database_button = tk.Button(
    window, text="Select Database File", command=select_database_path
)

calculate_button = tk.Button(window, text="Calculate DAT", command=run_calculate_dat)

window.mainloop()
