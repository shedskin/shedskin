# global variables, read and written from CPython (0921-B4, #1676); see README.md

counter = 0
name = 'start'
items = [1]
ratio = 0.5
_private = 1


def bump():
    global counter, name
    counter += 1
    name = 'bumped %d' % counter
    return counter


def get_counter():
    return counter


def get_name():
    return name


def get_items():
    return items


def half_ratio():
    return ratio / 2


if __name__ == '__main__':
    # bound only here, so not a module attribute on import (1113-B10)
    main_only = get_counter() + _private
    print(main_only)
    print(bump(), get_counter(), get_name(), get_items(), half_ratio())
