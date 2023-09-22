"""Model and functionality of a CSV correction-file

For lack of better name, that's what I've called it
"""
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
    """Representation of the entire CSV Correction file

    Attributes:
        data (list[CorrectionEntry]): 
            All parsed data rows from the input file (if they have an Object_ID or Host_ID)

        corrections_by_id (dict[str, CorrectionEntry): 
            The CorrectionEntries in self.data, indexed by ImageN_Object_ID.
            Note: objects present in multiple images will exist in this dictionary under
                  every applicable ID.
            Also note: sometimes, there are multiple rows representing the same objects; 
                  in this file, there are never conflicting registrations. If that is not
                  a strong guarantee in the general case, this logic should be amended

        object_id_to_image_id (dict[str, str]):
            Mapping between IDs in the columns Object_ID/Host_ID to the respective ImageN_Object_ID
            Note: a particular object_id can be referred to by multiple image object IDs; this 
                  mapping has picked *one* of them, subject to the whims of python dictionary
                  ordering. Since all the data is accessible by any IDs, it shouldn't matter in
                  practice, but if in the future, that distinction matters, this logic should
                  be amended

    This CorrectionFile can represent CSVs that were processed from an arbitrary number of images,
    not only 3, as in the example data.
    """

    def __init__(self, csv_file: Path):
        """CorrectionFile constructor

        Parameters:
            csv_path (Path): A path to a CSV file featuring corrections for processed Images
        """
        # Read in data where Object_ID and Host_ID are both specified
        with open(csv_file, encoding='utf-16') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            self._image_keys = {field for field in reader.fieldnames if re.match(r"Image\d_Object_ID", field)}
            self._row_model = CorrectionEntry.with_images(len(self._image_keys))
            self.data = [self._row_model.model_validate(r) for r in reader if r["Object_ID"] or r["Host_ID"]]

        ignore_values = {"0", ""}

        self.corrections_by_id = {
            getattr(entry, id_): entry
            for id_ in self._image_keys
            for entry in self.data
            if getattr(entry, id_) not in ignore_values and entry.host_id
        }

        self.object_id_to_image_id = {
            entry.object_id: getattr(entry, id_)
            for id_ in self._image_keys
            for entry in self.data
            if getattr(entry, id_) not in ignore_values
        }

    @property
    def num_images(self):
        """Get the number of image columns this CSV represents"""
        return len(self._image_keys)

