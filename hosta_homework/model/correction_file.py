import csv
from pathlib import Path
import re

from pydantic import BaseModel, Field, create_model


class CorrectionEntry(BaseModel):
    """Entry in the CSV file

    Subclass with class method CorrectionEntry.with_images,
    in case you ever wanted not exactly 3 image ID columns

    Instantiating this model directly assumes no images

    Similarly to hosta_homework.model.image_file.ImageFile,
    I'm only minimally documenting the Fields here, though
    in a production setting, would recommend it be more
    thorough.
    """
    family_and_type: str = Field(
            alias="Family and Type",
            title="Family and Type",
            description="...")

    height: str = Field(alias="Height")
    depth: str = Field(alias="Depth")
    width: str = Field(alias="Width")
    trim_length: str = Field(alias="Trim Length")
    area: str = Field(alias="Area")
    object_id: str = Field(alias="Object_ID")
    host_id: str = Field(alias="Host_ID")

    @classmethod
    def with_images(cls, num_images: int):
        """Create a version of CorrectionEntry with added ImageN_Object_ID fields

        Parameters:
          num_images (int): Number of 1-indexed image columns to add to a subclass

        Returns:
          A derived pydantic model including new fields
        """
        return create_model(
            f"CorrectionEntry{num_images}Img",
            __base__=cls,
            **{f"Image{i}_Object_ID":(str, ...) for i in range(1,num_images+1)}
        )


class CorrectionFile:

    def __init__(self, csv_file: Path):
        # Read in data where Object_ID and Host_ID are both specified
        with open(csv_file, encoding='utf-16') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            self._image_keys = {field for field in reader.fieldnames if re.match(r"Image\d_Object_ID", field)}
            self.row_model = CorrectionEntry.with_images(len(self._image_keys))
            self.data = [self.row_model.model_validate(r) for r in reader if r["Object_ID"] or r["Host_ID"]]

        ignore_values = {"0", ""}

        self.corrections_by_id = {
            getattr(entry, id_): entry
            for id_ in self._image_keys
            for entry in self.data
            if getattr(entry, id_) not in ignore_values
        }

        self.object_id_to_image_id = {
            entry.object_id: getattr(entry, id_)
            for id_ in self._image_keys
            for entry in self.data
            if getattr(entry, id_) not in ignore_values
        }

    @property
    def num_images(self):
        return len(self.image_keys)

