from itertools import chain
from framework import MySQLDatabase

from models import Human, Interface


MODELS = (
    Human,
    Interface,
)


def repl(locals={}):
    import code
    code.interact(local=locals)


def run():
    with MySQLDatabase(host='localhost', user='nothing', passwd='',
                       db='nothing', models=MODELS) as d:
        h = Human()
        i = Interface()

        repl(dict(chain(globals().items(), locals().items())))


if __name__ == '__main__':
    run()
