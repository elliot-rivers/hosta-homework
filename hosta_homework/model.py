import csv
from dataclasses import dataclass
import json
import logging
from operator import itemgetter
from pathlib import Path
import re
import typing
from uuid import UUID


from .dataclasses import FromDict


class CorrectionFile:

    def __init__(self, csv_file: Path):
        # Read in data where Object_ID and Host_ID are both specified
        with open(csv_file, encoding='utf-16') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            self.data = [r for r in reader if r["Object_ID"] or r["Host_ID"]]

        # Pull out object ids for every ImageN_Object_ID column
        # Flexible to support != 3 image files/columns
        #self.object_ids_by_image = {
        #    key: {row[key] for row in self.data if row[key] not in {"0", ""}}
        #    for key in self.data[0] if re.match(r"Image\d_Object_ID", key)
        #}
        self._image_keys = {key for key in self.data[0] if re.match(r"Image\d_Object_ID", key)}

        ignore_values = {"0", ""}

        self.corrections_by_id = {
            entry[id_]: entry
            for id_ in self._image_keys
            for entry in self.data
            if entry[id_] not in ignore_values
        }

        self.object_id_to_image_id = {
            entry['Object_ID']: entry[id_]
            for id_ in self._image_keys
            for entry in self.data
            if entry[id_] not in ignore_values
        }

    @property
    def num_images(self):
        return len(self.image_keys)


@dataclass
class ImageInfo(FromDict):
    file_name: str


@dataclass 
class Ops3D(FromDict):
    '''Dataclass representation of 3d objects in an image

    Note: inconsistent variable styling is preserved from the input file schema
    '''
    unique_id: str
    item_id: int
    imageIds: typing.List[str]

    def process_correction(self, correction_file: CorrectionFile, image_to_unique_id: typing.Dict[str, str]):
        try:
            correction = correction_file.corrections_by_id[str(self.item_id)]
            try:
                csv_host = correction["Host_ID"]
                image_id = correction_file.object_id_to_image_id[csv_host]
            except KeyError:
                print(f"Can't find csv host id '{csv_host}' in obj->img mapping {correction_file.object_id_to_image_id}")
                return self
            try: 
                unique_id = image_to_unique_id[image_id]
                return Ops3DWithParent(**self.__dict__, **{"parent_id": unique_id})
            except KeyError:
                print(f"Can't find image_id id '{image_id}' in img->unique mapping {image_to_unique_id}")
                return self
        except KeyError:
            return self


@dataclass 
class Ops3DWithParent(Ops3D):
    parent_id: str


@dataclass
class Image(FromDict):
    image_info: ImageInfo
    ops_3d: typing.List[Ops3D]

    def process_corrections(self, correction_file: CorrectionFile, image_to_unique_id: typing.Dict[str, str]):
        for i, entry in enumerate(self.ops_3d):
            self.ops_3d[i] = entry.process_correction(correction_file, image_to_unique_id)



class Room:

    @property
    def num_images(self):
        return len(self.images)

    def __init__(self, image_files: typing.List[str]):
        self.images = []
        for j in image_files:
            with open(j, "r") as f:
                data = json.load(f)
            self.images.append(Image.from_dict(data))

        self.image_id_to_unique_id = {
            str(op_3d.item_id): op_3d.unique_id 
                for image in self.images 
                    for op_3d in image.ops_3d
        }


    def process_corrections(self, csv_file: str):
        csv = CorrectionFile(csv_file)

        for image in self.images:
            image.process_corrections(csv, self.image_id_to_unique_id)
