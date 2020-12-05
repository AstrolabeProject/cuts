#
# Miscellaneous Utility Methods.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Port from Image MetaData ToolKit project.
#
import json
import operator
from functools import reduce


def get_in (a_dictionary, keys):
    """
    Get a nested value from the given dictionary indexed by the given sequence of keys.
    """
    dic = a_dictionary
    last_idx = len(keys) - 1
    for idx, key in enumerate(keys):
        val = dic.get(key)
        if (val is None):
            return None
        elif (idx >= last_idx):
            return val
        elif (isinstance(val, dict)):
            dic = val
        else:
            return None


def keep_characters (a_str, allowed=set()):
    """
    Return a new string formed from the given string by passing through only
    the characters in the, optionally specified, iterable 'allowed' collection.

    :param a_str: the string to be "filtered" by this method.
    :param allowed: an iterable of allowable characters for the returned string.
                    Default is the empty set (nothing allowed).
    """
    return ''.join(ch for ch in a_str if ch in allowed)


def keep (fn, collection):
    """
    Returns a list of the non-None results of (fn item). Note, this means False
    return values will be included. The function should be free of side-effects.
    """
    return list(filter(lambda x: x is not None, map(fn, collection)))


def missing_entries (a_dictionary, required=[]):
    """
    Look up each of the keys in the required key list and return a list of keys
    missing from the given dictionary.
    """
    missing = [ rkey for rkey in required if (rkey not in a_dictionary) ]
    return None if (len(missing) < 1) else missing


def product (iterable):
    """ Return the product of the numbers in the given iterable. """
    return reduce(operator.mul, iterable, 1)


def remove_entries (a_dictionary, ignore=[]):
    """
    Remove any entries whose keys are in the ignore list from the given dictionary.
    If not given, the ignore list defaults to an empty list.
    """
    for key in ignore:
        a_dictionary.pop(key, None)         # remove keyed entry: ignore key errors


def to_JSON (datadict, **json_kwargs):
    """
    Create and return a JSON string corresponding to the given data dictionary.

    :param json_kwargs: dictionary containing arguments to the json.dumps call.
    :return a JSON string
    """
    return json.dumps(datadict, **json_kwargs)
