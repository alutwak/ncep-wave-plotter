import sys


def message(msg):
    """ Prints a user message
    """
    print(msg, file=sys.stderr)


def info(msg):
    """ Prints info to be consumed by caller
    """
    print(msg, file=sys.stdout)
