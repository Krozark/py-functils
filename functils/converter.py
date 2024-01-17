__all__ = [
    "converter",
]


def converter(value, types=[], max_depth=-1, depth=0):
    """
    Convert a value into another one by casting the value of certain type into other. Can be called on iterable.
    types: list of tuple as [(Decimal, float),] where the first member wil be convert to the second one
    return : dict of same value but with casted types
    """
    if (depth < max_depth) or max_depth < 0:
        if isinstance(value, dict):
            value = {
                k: converter(v, types=types, max_depth=max_depth, depth=depth + 1)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            value = [
                converter(v, types=types, max_depth=max_depth, depth=depth + 1)
                for v in value
            ]
        elif isinstance(value, tuple):
            value = (
                converter(v, types=types, max_depth=max_depth, depth=depth + 1)
                for v in value
            )
        else:
            for _from, _to in types:
                if isinstance(value, _from):
                    value = _to(value)
                    break
    return value
