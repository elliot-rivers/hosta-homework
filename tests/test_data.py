"""As I make assumptions about the dataset, make sure they're true

...and record them for posterity
"""
from collections import Counter

from hosta_homework import data, model

def test_image_id_uniqueness():
    """ensure image IDs are not present in multiple ops_3d in any image"""
    room = model.Room(data.IMAGE_FILES)

    global_image_ids = []
    for image in room.images:
        image_ids = []
        for op_3d in image.ops_3d:
            # list->set->list to remove local duplicates
            image_ids += list(set(op_3d.imageIds))
        # set and list should be the same length if there are no duplicates
        assert len(image_ids) == len(set(image_ids))
        global_image_ids += image_ids

    print(Counter(global_image_ids))

    assert len(global_image_ids) == len(set(global_image_ids))


def test_item_id_in_image_ids():
    """Ensure that every item_id is in the list of imageIds for every ops_3d"""
    room = model.Room(data.IMAGE_FILES)

    for image in room.images:
        for op_3d in image.ops_3d:
            if op_3d.imageIds and op_3d.item_id:
                assert str(op_3d.item_id) in op_3d.imageIds
