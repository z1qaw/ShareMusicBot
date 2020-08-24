import dataclasses


@dataclasses.dataclass
class Artwork:
    width: int
    height: int
    url: str
    
    def __post_init__(self):
        self.url = self.url.replace('{w}', str(self.width)).replace('{h}', str(self.height))