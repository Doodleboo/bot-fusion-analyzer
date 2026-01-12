import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class GalleryMonthElement:
    message_id: str
    user_id: str
    dex_ids: str
    instances: int

    def __init__(self, message_id: str, user_id: str, dex_ids: str, instances: int):
        self.message_id = message_id
        self.user_id = user_id
        self.dex_ids = dex_ids
        self.instances = instances


# Gallery file format: nested dictionary
# user_id -> fusion_id -> message_id(s)


def get_gallery_month_list() -> list[GalleryMonthElement]:
    gallery_month_file = get_filename()
    try:
        with open(gallery_month_file, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except IOError:
        # Create the empty file, return empty list
        with open(gallery_month_file, 'x', encoding='utf-8') as f:
            json.dump([], f)
            return []


def get_filename() -> str:
    est_tz = ZoneInfo("America/New_York")
    now = datetime.now(est_tz)
    return get_gallery_month_path(f"GalleryCache_{now.year}_{now.month}.json")


def get_gallery_month_path(filename: str) -> str:
    return os.path.join(CURRENT_DIR, "..", "..", "data", "gallery-cache", filename)
