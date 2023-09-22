import logging
from pathlib import Path

from . import model
from . import data


if __name__ == "__main__":
    # Print out all logs
    logging.basicConfig(level=logging.INFO)

    room = model.Room(data.IMAGE_FILES)
    room.process_corrections(data.CSV_FILE)
    room.save_images(Path(__file__).parents[1] / "data" / "out")
