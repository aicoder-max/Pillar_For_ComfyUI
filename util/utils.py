def set_dict_value(data: dict, dict_key: str, value, create_missing_objects=True):
    """ Sets a deeply nested value given a dot-delimited key."""
    keys = dict_key.split('.')
    key = keys.pop(0) if len(keys) > 0 else None
    if key not in data:
        if create_missing_objects == False:
            return None
        data[key] = {}
    if len(keys) == 0:
        data[key] = value
    else:
        set_dict_value(data[key], '.'.join(keys), value, create_missing_objects)

    return data
