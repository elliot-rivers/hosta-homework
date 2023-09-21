import json

from . import model
from . import data


if __name__ == "__main__":
    room = model.Room(data.IMAGE_FILES)
    room.process_corrections(data.CSV_FILE)

    print(room.images[0])
