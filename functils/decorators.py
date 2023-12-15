def memorized_method(func):
    def wrapper(obj, *args, force=False, **kwargs):
        cache_attr = f"_memorized_method_cache_{func.__name__}"
        if not hasattr(obj, cache_attr) or force:
            result = func(*args, **kwargs)
            setattr(obj, cache_attr, result)
        return getattr(obj, cache_attr)

    return wrapper
