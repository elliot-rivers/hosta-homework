from argparse import ArgumentParser
import logging
import json
from pathlib import Path
from textwrap import dedent

from . import model
from . import data


OUT_DIR = Path(__file__).parents[1] / "data" / "out"

def main(log_level: int, force_overwrite: bool = False):
    logging.basicConfig(level=log_level)

    room = model.Room(data.IMAGE_FILES)
    room.process_corrections(data.CSV_FILE)
    room.save_images(OUT_DIR, force=force_overwrite)

def print_stats():
    num_ops_with_parents_now = 0

    for new_file in OUT_DIR.glob("*.json"):
        with open(new_file) as f:
            data = json.load(f)
        for op in data['ops_3d']:
            if 'parent_id' in op:
                num_ops_with_parents_now += 1

    logging.info("%d ops_3d were updated to include a parent link", num_ops_with_parents_now)

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
    print_stats()
