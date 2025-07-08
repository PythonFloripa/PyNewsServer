from pydantic import BaseModel
from enum import Enum
from typing import List


class TagEnum(str, Enum):
    bug_fix = "bug_fix"
    update = "update"
    deprecate = "deprecate"
    new_feature = "new_feature"
    security_fix = "security_fix"

class Subscription(BaseModel):
    tags: List[TagEnum]
    libraries_list: List[str]
