import dataclasses
from .ym_objects_set import ObjectsSet

@dataclasses.dataclass
class SearchQuery:
    text: str
    albums: ObjectsSet
    tracks: ObjectsSet
    artists: ObjectsSet
    counts: dict
