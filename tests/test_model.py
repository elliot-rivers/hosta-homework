import typing

from hosta_homework.data import CSV_FILE
from hosta_homework.model import CorrectionFile


def test_correction_csv_instantiation():
   c = CorrectionFile(CSV_FILE) 
   assert len(c.data)
