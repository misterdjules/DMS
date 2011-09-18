"""Modules used to gather every utility function
that is not present in the standard library.
PLEASE point me out the ones that actually are in
the standard library !"""

__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "8 August 2002"

def get_file_extension(filename):
    """Return a string that represent the file extension
    (including the leading period) of the file whose name is filename."""
    if '.' not in filename:
        return ""
    return "." + filename.split('.')[-1]

def strip_file_extension(input_file):
    """Return a string which is the file name without
    its trailing extension"""
    if "." not in input_file:
        return input_file
    return ".".join(input_file.split(".")[:-1])
