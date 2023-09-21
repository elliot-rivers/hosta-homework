"""Data models of system components

In particular:
    - ImageFile: representation of image json files
    - CorrectionFile: representation of csv files
    - Room: container representing all images in a room
"""

from .correction_file import CorrectionFile
from .image_file import ImageFile
from .room import Room

