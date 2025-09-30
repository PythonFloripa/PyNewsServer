from enum import Enum


class LibraryTagUpdatesEnum(str, Enum):
    UPDATE = "updates"
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    SECURITY_FIX = "security_fix"
