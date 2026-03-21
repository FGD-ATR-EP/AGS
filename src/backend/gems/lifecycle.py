from enum import Enum


class GemStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REVIEWED = "REVIEWED"
    SANDBOXED = "SANDBOXED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
