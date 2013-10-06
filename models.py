from framework import Model

from fields import VARCHAR, IPAddress


class Human(Model):
    _table_name = u'human'

    name = VARCHAR(10)


class Interface(Model):
    name = VARCHAR(255)
    ip = IPAddress(ip_type=4)
