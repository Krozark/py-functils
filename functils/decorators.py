def memorized_method(func):
    """
    This decorator allow a user to cache a method call of an object (with no parameters).
    The `force` parameter allow to update the cache value.
    Internally, the first time the function is called (or when force°True), the returned value is stored in a new member.
    Then, each new call will use the value stored in the cache.

    ```python
    class A:
        @memorized_method
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

    def wrapper(obj, force=False):
        cache_attr = f"_memorized_method_cache_{func.__name__}"
        if not hasattr(obj, cache_attr) or force:
            result = func(obj, force=force)
            setattr(obj, cache_attr, result)
        return getattr(obj, cache_attr)

    return wrapper
