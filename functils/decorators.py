def memorized_method(func):
    def wrapper(obj, force=False):
        cache_attr = f"_memorized_method_cache_{func.__name__}"
        if not hasattr(obj, cache_attr) or force:
            result = func(obj, force=force)
            setattr(obj, cache_attr, result)
        return getattr(obj, cache_attr)

    return wrapper
