import sqlite3
import os
from .utils import relative_to


db_path = relative_to(__file__,"DB.db")

con = sqlite3.connect(db_path, check_same_thread=False)
