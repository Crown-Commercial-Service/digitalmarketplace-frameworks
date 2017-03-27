def merge_schemas(a, b):
    if not (isinstance(a, dict) and isinstance(b, dict)):
        raise TypeError("Error merging unsupported types '{}' and '{}'".format(
            type(a).__name__, type(b).__name__
        ))

    result = a.copy()
    for key, val in b.items():
        if isinstance(result.get(key), dict):
            result[key] = merge_schemas(a[key], val)
        elif isinstance(result.get(key), list):
            result[key] = result[key] + val
        else:
            result[key] = val

    return result


def empty_schema(schema_name):
    return {
        "title": "{} Schema".format(schema_name),
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "additionalProperties": False,
        "properties": {},
        "required": [],
    }
