# config.py -- where the input and output folders are.

import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")        # input poems go here
OUTPUT_DIR = os.path.join(HERE, "outputs")   # figures are saved here
POEMS_CSV = os.path.join(DATA_DIR, "poems.csv")
