from nothing.fields import StrippedVARCHAR, IPAddress
from nothing.framework import Model


class Human(Model):
    _table_name = 'human'

    name = StrippedVARCHAR(10)


class Interface(Model):
    name = StrippedVARCHAR(255)
    ip = IPAddress()
