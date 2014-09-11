import ipaddress

from .framework import Field


class _int_base(Field):
    def __init__(self, default=0, **kwargs):
        self.value = default
        super(Int, self).__init__(**kwargs)

    def clean(self, value):
        if 2**(self.bits-1) <= value <= 2**(self.bits-1) - 1:
            return value
        else:
            raise ValueError('% value out of range' % self.__class__.__name__)


class TINYINT(_int_base):
    bits = 8
    column_info = {'mysql': 'TINYINT'}


class SMALLINT(_int_base):
    bits = 16
    column_info = {'mysql': 'SMALLINT'}


class INT(_int_base):
    bits = 32
    column_info = {'mysql': 'INT'}


class BIGINT(_int_base):
    bits = 64
    column_info = {'mysql': 'BITINT'}


class VARCHAR(Field):
    def __init__(self, max_length, default='', **kwargs):
        super(VARCHAR, self).__init__(**kwargs)
        self.max_length = max_length
        self.value = default

    def clean(self, value):
        if not isinstance(value, str):
            raise ValueError('Invalid VARCHAR value')
        value = str(value) # If bytes, assume ASCII.

        if len(value) > self.max_length:
            raise ValueError('VARCHAR value longer than maximum length (%s)'
                             % self.max_length)

        return value

    @property
    def column_info(self):
        return {'mysql': 'VARCHAR(%s)' % self.max_length}


class StrippedVARCHAR(VARCHAR):
    def clean(self, value):
        value = super(StrippedVARCHAR, self).clean(value)
        return value.strip()


class IPAddress(Field):
    def clean(self, value):
        return ipaddress.ip_address(value)

    def to_db(self, db, value):
        ip_int = int(self.value)
        return {
            'upper': ip_int >> 64,
            'lower': ip_int & (2**64 - 1)
        }

    def from_db(self, db, columns):
        return self.clean((columns['upper'] << 64) | columns['lower'])

    column_info = {
        'mysql': (
            ('upper', 'BIGINT UNSIGNED'),
            ('lower', 'BIGINT UNSIGNED')
        )
    }
