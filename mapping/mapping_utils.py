"""This module provides functionality for mapping numbers using a notched distribution.

The module implements a number mapping system that transforms uniformly distributed
random numbers into a distribution with a central notch - creating numbers that are
close to, but never exactly, the center value. This is used to generate metronome
timings that are almost, but never quite, one second apart.
"""

import os
import random

MIN_ZERO = 0.50
MAX_ZERO = 0.99
MIN_ONE = 1.01
MAX_ONE = 1.50
MIN_MARK_LOW = 0.30
MAX_MARK_LOW = 0.40
MIN_MARK_HIGH = 1.60
MAX_MARK_HIGH = 1.70

MAPPING = []


def set_mapping(mapping):
    """Set the global mapping to a new value.
    Args:
        mapping: A list of tuples where each tuple contains a float and a corresponding weight.
    """
    global MAPPING
    MAPPING = mapping
    
def load_mapping(filename='mapping.csv'):
    """Load the mapping from a CSV file.

    Args:
        filename: The name of the CSV file containing the mapping data.
    """
    global MAPPING
    MAPPING = []
    with open(filename, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) == 2:
                MAPPING.append((float(values[0]), float(values[1])))
                
def map_number(input_number: float) -> float:
    """Maps a number between 0.0 and 1.0 to a weighted value using a notched
    distribution.

    Args:
        input_number: A float between 0.0 and 1.0 to be mapped

    Returns:
        float: The mapped value according to the notched distribution mapping table
    """
    for entry in MAPPING:
        if entry[0] >= input_number:
            return entry[1]
    return 1.00

def zero(skew=0):
    dur = (0.5 + map_number(random.random())) - skew
    if skew > 0:
        dur -= abs(skew)
    else:
        dur -= skew
    if not is_zero(dur):
        dur = zero(skew/2)
    return dur

def one(skew=0):
    dur = 0.5 + map_number(random.random())
    if skew < 0:
        dur += abs(skew)
    else:
        dur -= skew
    dur = min(1.5, dur)
    if not is_one(dur):
        dur = one(skew/2) 
    return dur
    
def mark(skew=0):
    dur = 0.5 + map_number(random.random())
    val = 1.6 if dur > 1 else 0.40 

    if dur < 1:
        return MIN_MARK_LOW
    else:
        return MAX_MARK_HIGH

def is_zero(val):
    return val < MAX_ZERO and val > MIN_ZERO

def is_one(val):
    return val > MIN_ONE and val < MAX_ONE

def is_mark(val):
    return (val < MAX_MARK_LOW and val > MIN_MARK_LOW) or (val < MAX_MARK_HIGH and val > MIN_MARK_HIGH)

