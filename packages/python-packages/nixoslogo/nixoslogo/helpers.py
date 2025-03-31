import hashlib

import jsonpickle


def stable_hash(thing):
    dump = jsonpickle.encode(thing)
    return hashlib.md5(dump.encode("utf-8")).digest().hex()
