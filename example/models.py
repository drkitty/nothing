from nothing.fields import VARCHAR, IPAddress
from nothing.framework import Model


class Human(Model):
    _table_name = 'human'

    name = VARCHAR(10)


class Interface(Model):
    name = VARCHAR(255)
    ip = IPAddress()
