

def computed_property(dependencies):
    """
    Decorator to cache a class property, recalculating only if one of the dependencies changes.
    Supports getter, setter, and deleter like the property decorator.
    """
    def decorator(func):
        cache_attr = f'_cached_{func.__name__}'
        last_values_attr = f'_last_values_{func.__name__}'

        class CachedProperty:
            def __init__(self, func):
                self.func = func
                self.__doc__ = func.__doc__  # Copy the docstring

                self._setter = None
                self.__setter_doc__ = None

                self._deleter = None
                self.__deleter_doc__ = None

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                last_values = getattr(instance, last_values_attr, None)
                current_values = tuple(getattr(instance, dep) for dep in dependencies)

                if last_values is not None and last_values == current_values:
                    return getattr(instance, cache_attr)

                # Calculate new value and cache it
                result = self.func(instance)
                setattr(instance, cache_attr, result)
                setattr(instance, last_values_attr, current_values)
                return result

            def __set__(self, instance, value):
                if self._setter:
                    self._setter(instance, value)
                else:
                    raise AttributeError(f"Can't set attribute '{self.func.__name__}' directly")

            def __delete__(self, instance):
                if self._deleter:
                    self._deleter(instance)
                if hasattr(instance, cache_attr):
                    delattr(instance, cache_attr)
                if hasattr(instance, last_values_attr):
                    delattr(instance, last_values_attr)

            def setter(self, setter_func):
                self._setter = setter_func
                self._setter.__doc__ = setter_func.__doc__ 
                return self

            def deleter(self, deleter_func):
                self._deleter = deleter_func
                self._deleter.__doc__ = deleter_func.__doc__ 
                return self

        return CachedProperty(func)

    return decorator


if __name__ == "__main__":
    # Usage Example
    class Circle:
        def __init__(self, radius=1, color="Blue"):
            self.radius = radius
            self.color = color

        @computed_property(dependencies=['radius'])
        def diameter(self):
            """Calculate circle diameter"""
            print("Recalculating Diameter")
            return self.radius * 2

        @diameter.setter
        def diameter(self, diameter):
            """Setting diameter readjust radius"""
            self.radius = diameter / 2

        @diameter.deleter
        def diameter(self):
            """Deletes radius"""
            self.radius = 0


    # Testing the cache behavior
    obj = Circle(2, "Yellow")
    print(obj.diameter)  # Should print "Recalculating diameter" and return 4
    print(obj.diameter)  # Should return 4 without recalculating

    obj.color = "Blue" # Changing one of atributes
    print(obj.diameter)  # Should return 4 without recalculating

    obj.radius = 3       # Changing one of the dependencies
    print(obj.diameter)  # Should print "Recalculating diameter" and return 6
    print(obj.diameter)  # Should return 6 without recalculating

    obj.diameter = 10    # Using setter, updates radius
    print(obj.radius)    # Should return 5
    print(obj.diameter)  # Should print "Recalculating diameter" and return 10

    del obj.diameter     # Using deleter, resets radius to 0
    print(obj.diameter)  # Should print "Recalculating diameter" and return 0

    print()
    print(Circle.diameter.__doc__)  # Should print "Calculate circle diameter"
    print(Circle.diameter._setter.__doc__)  # Should print "Setting diameter readjust radius"
    print(Circle.diameter._deleter.__doc__)  # Should print "Deletes radius"