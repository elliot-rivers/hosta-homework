from argparse import ArgumentParser
import logging
from pathlib import Path
from textwrap import dedent

from . import model
from . import data


def main(log_level: int, force_overwrite: bool = False):
    logging.basicConfig(level=log_level)

    room = model.Room(data.IMAGE_FILES)
    room.process_corrections(data.CSV_FILE)
    room.save_images(Path(__file__).parents[1] / "data" / "out", force=force_overwrite)

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="hosta_homework",
        description=dedent("""\
            Process image files and a correction CSV into output files. 

            All the input files are hard-coded for the sake of this example:
                inputs are processed from data/ and emitted to data/out/"""),
        )

    parser.add_argument(
        "--log-level",
        choices=logging.getLevelNamesMapping().keys(),
        default="INFO",
        help="Specify which log level to emit at. Default: INFO")

    parser.add_argument(
        "--force-overwrite",
        action="store_true",
        help="Set this flag if you want to force output file clobbering")

    args = parser.parse_args()

    log_level = logging.getLevelNamesMapping()[args.log_level]
    main(log_level, args.force_overwrite)
