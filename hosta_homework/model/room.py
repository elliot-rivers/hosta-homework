import typing

from .image_file import ImageFile


class Room:

    def __init__(self, image_files: typing.List[str]):
        self.images = []
        for j in image_files:
            with open(j, "r") as f:
                data = f.read()
            self.images.append(ImageFile.model_validate_json(data))

