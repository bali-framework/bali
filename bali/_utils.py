import re
from typing import Callable

from grpc import Server


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner


ServiceAdderNamePattern = re.compile(r"^add_.*_to_server$")


def get_service_adder(module) -> Callable[[object, Server], None]:
    namespace = vars(module)
    for i in dir(module):
        if ServiceAdderNamePattern.match(i):
            return namespace[i]


def pluralize(noun):
    """pluralize a given word

    ref:
    https://www.codespeedy.com/program-that-pluralize-a-given-word-in-python/

    :param noun:
    :return:
    """
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[aeiou]y$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'
