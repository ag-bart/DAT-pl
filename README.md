# Divergent Association Task - Polish adaptation

The Polish Divergent Association Task (DAT) Adaptation project is designed to bring the DAT, a measure of verbal creativity and divergent thinking, to the Polish language. 

DAT involves generating 10 words that are as different from each other as possible. This project facilitates the administration and scoring of the task in Polish, providing a tool for researchers exploring creativity in participants' native language.

## About DAT


The DAT score is calculated based on the average distance between the given words. The distances are determined by analyzing how often words are used together in similar contexts, utilizing pre-trained GloVe model.

Words with closer associations have smaller distances. Creative ability is associated with thinking of words that are more unrelated to each other, resulting in a higher DAT score.



Read the authors' [manuscript](https://www.pnas.org/content/118/25/e2022340118) to learn more about the task. 



## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ag-bart/datpl.git
   cd datpl
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the setup script:
    ```bash
    sh setup.sh
    ```

   This script performs the following tasks:

   - Downloads the GloVe model and unpacks it.
   - Filters words and vectors from the GloVe model, retaining only those found in the included dictionary file (words.txt).
   - Creates an SQLite database using the filtered words and vectors.
   - Performs tests to ensure the database is correctly configured.
   - Removes temporary files, leaving only the database if tests pass.
  

## Configuration
### Data File
In the `config.ini` file, you can specify the path to the data file for computation. Locate the `[Data]` section and update the `data_file_path` setting accordingly.

   ```ini
   [Data]
    data_file_path = data/dat-data.xlsx
   ```

## Running the Jupyter Notebook

1. Launch Jupyter Notebook:
   ```bash
   cd datpl
   jupyter notebook
   ```

2. Open the `example_notebook.ipynb` file in the Jupyter interface.

3. Run the notebook cells one by one or use the "Run All" option.


## Credits

Global Vectors for Word Representation by:
Dadas, S. (2019). Polish NLP resources (Version 1.0) [Computer software]. https://github.com/sdadas/polish-nlp-resources

Olson, J. A., Nahas, J., Chmoulevitch, D., Cropper, S. J., & Webb, M. E. (2021). Naming unrelated words predicts creativity. Proceedings of the National Academy of Sciences of the United States of America, 118(25). https://doi.org/10.1073/pnas.2022340118
