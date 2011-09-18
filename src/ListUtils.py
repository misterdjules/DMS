"""Modules used to gather every utility function
that is not present in the standard library.
PLEASE point me out the ones that actually are in
the standard library !"""

__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "8 August 2002"

def get_intersection(list_a, list_b):
    """Return a list containaing the elements
    that are in both lists"""
    intersection = []
    for elem in list_a:
        if elem in list_b:
            intersection.append(elem)
    return intersection
