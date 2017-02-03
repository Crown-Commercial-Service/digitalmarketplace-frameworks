def merge_schemas(a, b):
    if not (isinstance(a, dict) and isinstance(b, dict)):
        raise ValueError("Error merging '{}' and '{}'".format(
            type(a).__name__, type(b).__name__
        ))

    result = a.copy()
    for key, val in b.items():
        if isinstance(result.get(key), dict):
            result[key] = merge_schemas(a[key], b[key])
        elif isinstance(result.get(key), list):
            result[key] = result[key].copy()
            result[key].extend(val)
        else:
            result[key] = val

    return result
