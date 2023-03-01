import os
import logging

from dataclasses import dataclass, field

logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG if os.getenv("DEBUG", False) else logging.INFO)


@dataclass
class Guest:
    id: str = field(init=False)
    name: str
    last_name: str
    plus_one: bool = False

    def __post_init__(self):
        self.id = f"{self.name}:{self.last_name}"
