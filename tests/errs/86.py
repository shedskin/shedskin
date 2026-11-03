class C:
    def __enter__(self):
        return (1, 2)
    def __exit__(self, a, b, c):
        pass

with C() as (a, b):
    pass

#*ERROR* 86.py:7: unsupported 'with' target (only a plain name is supported)
