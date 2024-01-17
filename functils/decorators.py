__all__ = ["memorized_method"]


class memorized_method:
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

    def __init__(self, cache_key=None):
        self._cache_key = cache_key

    def __call__(self, func):
        if not self._cache_key:
            self._cache_key = self.get_cache_key(func)

        def wrapper(obj, *args, force=False, **kwargs):
            if not hasattr(obj, self._cache_key) or force:
                result = func(obj, *args, **kwargs)
                setattr(obj, self._cache_key, result)
            return getattr(obj, self._cache_key)

        wrapper._cache_key = self._cache_key

        return wrapper

    @staticmethod
    def get_cache_key(func):
        # deal with this function called on methode decorated with @cache()
        if hasattr(func, "_cache_key"):
            return func._cache_key

        cache_key_prefix = "_cache"
        cache_key_name = (
            func.__name__[4:] if func.__name__.startswith("get_") else func.__name__
        )

        return "_".join([cache_key_prefix, cache_key_name])
