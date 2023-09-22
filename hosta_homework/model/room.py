"""Data model of a Room of images"""
import logging
from os import PathLike
from pathlib import Path
import typing

from .image_file import ImageFile
from .correction_file import CorrectionFile


class Room:
    """Representation of a room of images and associated objects

    Attributes:
        images (list[ImageFile]): 
            A list of the parsed ImageFiles that make up the room

        image_id_to_unique_id (dict[str, UUID]): 
            A dictionary mapping between image_ids and unique_ids.
            Needed for correction processing, as the csv files refer
            to image-ids only, but the output json should employ unique-ids
    """

    def __init__(self, image_files: typing.List[PathLike]):
        """Room constructor

        This object parses the provided image json files into a list of
        ImageFile objects. Additionally, it extracts a mapping of image-ids
        to unique-ids for use during correction processing.

        Parameters:
            image_files (list[PathLike]): List of images file paths that comprise the room
        """
        self.images = []
        for j in image_files:
            with open(j, "r") as f:
                data = f.read()
            self.images.append(ImageFile.model_validate_json(data))

        self.image_id_to_unique_id = {
            str(op_3d.item_id): op_3d.unique_id 
                for image in self.images 
                    for op_3d in image.ops_3d
        }


    def process_corrections(self, csv_file: PathLike):
        """Given a csv corrections file, process them into the contained images

        It is assumed that the number of image object columns in the CSV file
        will equal the number of images that comprise the room.

        Parameters:
            csv_file (PathLike): Path to a csv file to process
        """
        csv = CorrectionFile(csv_file)

        if csv.num_images != len(self.images):
            raise ValueError(f"Correction file processed a different number of images ({csv.num_images}) than comprise this Room ({len(self.images)})!")

        for image in self.images:
            image.process_corrections(csv, self.image_id_to_unique_id)


    def save_images(self, output_dir: PathLike, force: bool = False):
        for image in self.images:
            out_filepath = (Path(output_dir) / image.image_info.file_name).with_suffix(".json")
            if out_filepath.exists() and not force:
                raise ValueError(f"Desired output filepath {out_filepath} already exists and force==False")
            logging.info("Saving %s...", out_filepath)
            json_str = image.model_dump_json(exclude_unset=True, indent=2)
            with open(out_filepath, "w") as f:
                f.write(json_str)

