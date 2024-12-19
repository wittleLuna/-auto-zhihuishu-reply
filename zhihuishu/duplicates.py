import json
import pandas as pd

def remove_duplicates_dicts(list_of_dicts):
    seen = set()
    result = []
    for d in list_of_dicts:
        # 将字典转换为 JSON 字符串
        s = json.dumps(d, sort_keys=True)
        if s not in seen:
            seen.add(s)
            result.append(d)
    return result
