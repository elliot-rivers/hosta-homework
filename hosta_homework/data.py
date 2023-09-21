from pathlib import Path


_data_dir = Path(__file__).parents[1] / "data"

IMAGE_FILES = [
    _data_dir / "3d3fde25-fc47-47ad-bda4-0b438196045b.json",
    _data_dir / "763fdd40-9408-45bb-b532-3f90b5c7c5d1.json",
    _data_dir / "b73070b3-7625-4975-872a-967b2297a458.json",
    ]


CSV_FILE = _data_dir / "EXP_ObjectID_HostID.csv"

