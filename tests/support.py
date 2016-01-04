try:
    import __builtin__ as builtins
except ImportError:
    # Python 3...
    import builtins

"""
This module exists to override the open function and log
what files get opened.
"""

opened_files = []


def clear_buffer():
    global opened_files
    opened_files = []


oldopen = builtins.open


def newopen(*args):
    global opened_files
    fh = oldopen(*args)
    opened_files.append(fh.name)
    return fh

builtins.open = newopen