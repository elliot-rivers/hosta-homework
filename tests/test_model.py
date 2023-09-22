import json

import pytest

from hosta_homework.data import IMAGE_FILES, CSV_FILE
from hosta_homework.model import CorrectionFile, ImageFile, Room


@pytest.mark.parametrize("image_file", IMAGE_FILES)
def test_image_file_completeness(image_file):
    """Test that the data model completely represents all the Image files

    Methodology:
      1. Deserialize the image files to json
         This demonstrates that the model can represent the data,
         but it does not show that it's a complete representation; thus:
      2. Serialize the model back to json, omitting unset parameters then re-read
         If this worked correctly, then we should have a dictionary that
         is equivalent to the input json.
      3. Load the original json string with the `json` module and compare them
         If they are the same, then we prove we can deserialize and serialize
         without introducing errors or unnecesssary fields
    """
    with open(IMAGE_FILES[0], "r") as f:
        json_str = f.read()
    image = ImageFile.model_validate_json(json_str)
    assert json.loads(image.model_dump_json(exclude_unset=True)) == json.loads(json_str)


def test_room():
    room = Room(IMAGE_FILES)
    assert len(room.images) == 3


def test_correction_file():
    cf = CorrectionFile(CSV_FILE)
