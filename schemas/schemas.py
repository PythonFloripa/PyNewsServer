from pydantic import BaseModel, field_validator
from typing import List


ALLOWED_TAGS_SUBSCRIPTION = {"bug_fix", "update", "deprecate", "new_feature", "security_fix"}

class Subscription(BaseModel):
    tags: List[str]
    libraries_list: List[str]

    @field_validator("tags")
    def validate_tags(cls, tags):
        invalid = [tag for tag in tags if tag not in ALLOWED_TAGS_SUBSCRIPTION]
        if invalid:
            raise ValueError(
                f"Tags inválidas: {invalid}. As opções permitidas são: {ALLOWED_TAGS_SUBSCRIPTION}"
            )
        return tags
