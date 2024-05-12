
import os
from typing import List
from console import warning


def mkdir_p(path):
    # check if directory exists
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Guard
            raise exc
    else:
        return

def vcd(path):
    return os.path.join(path, "..")

def ellipsis(str, maxlen=40):
    if len(str) > maxlen:
        return str[:maxlen] + "..."
    return str

def course_filter(allowed: List[str]):
    def fn(course: dict):
        if allowed:
            keep = False
            if any([course["course_code"].lower().startswith(prefix.lower()) for prefix in allowed]):
                keep = True
            elif str(course["id"]) in allowed:
                keep = True

            if not keep:
                return False
        return True
    return fn