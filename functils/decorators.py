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

    def __init__(self, cache_name=None):
        self._cache_name = cache_name

    def __call__(self, func):
        if not self._cache_name:
            self._cache_name = self.get_cache_name(func)

        def wrapper(obj, force=False):
            if not hasattr(obj, self._cache_name) or force:
                result = self.call_wrapped(obj, func, force=force)
                setattr(obj, self._cache_name, result)
            return getattr(obj, self._cache_name)

        wrapper._cache_name = self._cache_name
        return wrapper

    @staticmethod
    def get_cache_name(func):
        # deal with this function called on methode decorated with @memorized_method()
        if hasattr(func, "_cache_name"):
            return func._cache_name
        return f"_cache_{func.__name__}"

    def call_wrapped(self, obj, func, *args, **kwargs):
        """
        helper for mock test that only wrappe the function to call
        """
        return func(obj, *args, **kwargs)
