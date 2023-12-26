__all__ = ["get_cache_name", "memorized_method"]


def get_cache_name(func):
    f = func
    # deal with this function called on methode decorated with @memorized_method
    if hasattr(func, "_cache_name"):
        f = func._cache_name
    return f"_cache_{f.__name__}"


def memorized_method(cache_name=None):
    """
    This decorator allow a user to cache a method call of an object (with no parameters).
    The `force` parameter allow to update the cache value.
    Internally, the first time the function is called (or when force°True), the returned value is stored in a new member.
    Then, each new call will use the value stored in the cache.

    ```python
    class A:
        @memorized_method()
        def func(self, force=False):
            print("func called")
            value = ... # expensive computation
            return value

    a = A()
    a.func()
    # func called
    # value
    a.func()
    # value
    ```
    """

    def _memorized_method(func):
        cache = cache_name or get_cache_name(func)

        def wrapper(obj, force=False):
            if not hasattr(obj, cache) or force:
                result = func(obj, force=force)
                setattr(obj, cache, result)
            return getattr(obj, cache)

        wrapper._cache_name = cache
        return wrapper

    return _memorized_method
