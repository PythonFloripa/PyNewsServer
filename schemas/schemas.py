from pydantic import BaseModel
from typing import List, Literal


class Subscription(BaseModel):
    tags: Literal["bug_fix","update","deprecate","new_feature","security_fix"]
    libraries_list: List[str]
