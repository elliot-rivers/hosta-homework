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
import typing
from uuid import UUID

from pydantic import BaseModel, Field


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

    image_info: ImageInfo = Field(
            title="Image Info",
            description="Metadata about the images represented by this file")

    ops_3d: typing.List[Op3D] = Field(
            title="Ops 3D",
            description="Objects identified in the image by ML models")

