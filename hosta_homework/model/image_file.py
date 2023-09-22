"""Data model of the input image json files

Representing these as pydantic models streamlines validation and de/serialization.

General note: the objective of this exercise is NOT to question the data model,
but with some additional insight into the image file/op3ds generation, I highly suspect
that we could produce a more accurate / useful model with different formal classes of
Op3D or Detection etc.

Such a thing could look like:

class ImageFile(BaseModel):

    class Op3D(BaseModel):
        # Common things here
        unique_id: str

    class FooOp3D(Op3D):
        # addtl things
        specific_thing_1: str

    class BarOp3D(Op3D):
        # addtl things
        specific_thing_2: str

    ...

    ops_3d: List[FooOp3D | BarOp3D | ...]

This would make the model much more robust and useful
"""
import logging
from textwrap import dedent
import typing
from uuid import UUID

from pydantic import BaseModel, Field

from .correction_file import CorrectionFile


class ImageFile(BaseModel):
    """Model of an entire image file json schema to be interpreted by the system

    Note: As a demonstration, I have verbosely specified the fields in ImageInfo
          If this were a real model/schema, I would highly recommend full 
          documentation of all of the fields, but I have neither the time nor
          the insight to do so.
    """

    class ImageInfo(BaseModel):
        """Model of image metadata within an image file"""
        file_name: str = Field(
                title="File Name",
                description="The name of the analyzed image which produced this data")

        width: int = Field(
                title="Width",
                description="Width of the analyzed image, in pixels")

        height: int = Field(
                title="Width",
                description="Width of the analyzed image, in pixels")

        scale: float = Field(
                title="Scale",
                description="Proportional scale of the analyzed image")


    # See ImageFile.__doc__ as to why things below here are less verbosely defined

    class Op3D(BaseModel):
        """(Naive) Model of elements in ops_3d[]"""

        class Detection(BaseModel):
            """(Naive) Model of elements in ops_3d[].detections[]"""
            unique_id: UUID
            subcategory: str
            quantity_field: str
            width: float | None
            height: float | None
            centre: float | None
            unit: str | None
            quantity: float | None

        class UnoccludeDetection(BaseModel):
            """(Naive) Model of elements in ops_3d[].detections_unocclude[]"""
            unique_id: UUID
            subcategory: str
            quantity: float
            material_proportion: int

        supercategory: str
        unique_id: UUID
        item_id: int | None = None
        parent_id: UUID | None = None
        sqft: float | None = None
        imageIds: typing.List[str] | None = None
        bottom_width_left: typing.List[float] | None = None
        bottom_width_right: typing.List[float] | None = None
        height_bottom: typing.List[float] | None = None
        height_top: typing.List[float] | None = None
        width: float | None = None
        height: float | None = None
        centre: typing.List[float] | None = None
        unit: str | None = None
        quantity: float | int | None = None
        quantity_field: str | None = None
        baseboard: bool | None = None
        chair_guard: bool | None = None
        wall_protection: bool | None = None
        molding: bool | None = None
        corner_guard: bool | None = None
        wall_type: str | None = None # No example; assuming string
        detections: typing.List[Detection] | None = None
        detections_unocclude: typing.List[UnoccludeDetection] | None = None
        length: float | None = None # No example; assuming float
        level: int | None = None
        perimeter: float | None = None
        thickness: float | None = None # No example; assuming float
        thickness_bottom: float | None = None # No example; assuming float
        thickness_top: float | None = None # No example; assuming float
        totalArea: float | None = None
        depth: float | None = None
        depth_back: typing.List[float] | None = None
        depth_front: typing.List[float] | None = None
        parent_structure: str | None = None
        subcategory: str | None = None

        def process_correction(
                self, 
                correction_file: CorrectionFile, 
                image_to_unique_id: typing.Dict[str, str]
            ):
            """Process corrections for this Op3D

            Parameters:
                correction_file (CorrectionFile):
                image_to_unique_id (dict[str, str]):

            Assumptions:
            
              From analyzing the data files, I found that for any image file, I_n,
              in which an object, O, exists:
                - Its image-local record, O_n, contains a unique item_id
                - the set of item_ids across {I_1, ..., I_n} are always fully
                  represented in ImageIds, with some duplication
                - The set of item_ids across {I_1, ..., I_n} are always fully
                  represented in ImageN_Object_ID fields

              Therefore, I can create a map of {item_id -> op_3d} and intersect
              it with all correction entries by the same item_id and be guaranteed
              not to leave trivial updates unprocessed.

              In other words: if I check for corrections on all Op3ds, I should
              get them all.

            Steps:

              1. From the correction file, get any correction for this Op3d's item_id
              2. Get the host_id of the correction and convert it to a pertinent Image ObjectId
              3. Convert the ObjectId to a unique_id by cross-referencing with the image files

              (If any step fails a lookup, log a message and make no changes)
            """
            # Broken into multiple try/except blocks for tracing/logging convenience

            ## Step 1: Get correction
            # Cast to str because of inconsistencies in the data format
            id_key = str(self.item_id)
            try:
                correction = correction_file.corrections_by_id[id_key]
            except KeyError:
                logging.info("Nothing to correct for id: %s", id_key)
                return

            ## Step 2: Correction.HostID -> ObjectId
            try: 
                parent_host_id = correction.host_id
                parent_image_id = correction_file.object_id_to_image_id[parent_host_id]
            except KeyError:
                logging.warn(dedent("""\
                    Cannot convert CSV host_id '%s' to Image_ObjectId
                        (In processing item_id, '%s')"""),
                    parent_host_id,
                    id_key)
                return

            ## Step 3: ObjectId -> unique_id
            try: 
                unique_id = image_to_unique_id[parent_image_id]
            except KeyError:
                logging.warn(dedent("""\
                    Cannot convert CSV Image_ObjectId '%s' to unique_id
                        (In processing item_id, '%s' with parent Image_ObjectId, '%s')"""),
                    parent_image_id,
                    id_key,
                    parent_host_id)
                return

            # Update field in self so that it will be serialized
            self.parent_id = unique_id
            logging.info(dedent("""\
                Successfully updated Op3D record: 
                    Op3D.unique_id: %s
                    Op3D.item_id: %s
                    Op3D.parent_id: %s
                    parent Host_ID: %s
                    parent Object_ID: %s
                """),
                str(self.unique_id),
                id_key,
                unique_id,
                parent_host_id,
                parent_image_id)
                    


    image_info: ImageInfo = Field(
            title="Image Info",
            description="Metadata about the images represented by this file")

    ops_3d: typing.List[Op3D] = Field(
            title="Ops 3D",
            description="Objects identified in the image by ML models")


    def process_corrections(
            self,
            correction_file: CorrectionFile,
            image_to_unique_id: typing.Dict[str, str]
        ):
        """Process corrections for ops_3d in this image

        Loop over ops_3d and delegate processing to its process_correction method

        Parameters:
            correction_file (CorrectionFile):
            image_to_unique_id (dict[str, str]):
        """
        logging.info("Processing corrections for image file, '%s'", self.image_info.file_name)
        for op_3d in self.ops_3d:
            op_3d.process_correction(correction_file, image_to_unique_id)

