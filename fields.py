import ipaddr
from framework import Field


class _int_base(Field):
    def __init__(self, default=0, **kwargs):
        self.value = default
        super(Int, self).__init__(**kwargs)

    def clean(self, value):
        if 2**(self.bits-1) <= value <= 2**(self.bits-1) - 1:
            return value
        else:
            raise ValueError(u'% value out of range' % self.__class__.__name__)


class TINYINT(_int_base):
    bits = 8
    column_info = {u'mysql': u'TINYINT'}


class SMALLINT(_int_base):
    bits = 16
    column_info = {u'mysql': u'SMALLINT'}


class INT(_int_base):
    bits = 32
    column_info = {u'mysql': u'INT'}


class BIGINT(_int_base):
    bits = 64
    column_info = {u'mysql': u'BITINT'}


class VARCHAR(Field):
    def __init__(self, max_length, default=u'', **kwargs):
        super(VARCHAR, self).__init__(**kwargs)
        self.max_length = max_length
        self.value = default

    def clean(self, value):
        if not isinstance(value, basestring):
            raise ValueError(u'Invalid VARCHAR value')
        value = unicode(value) # if str, assume ASCII

        if len(value) > self.max_length:
            raise ValueError(u'VARCHAR value longer than maximum length (%s)'
                             % self.max_length)

        return value

    @property
    def column_info(self):
        return {u'mysql': u'VARCHAR(%s)' % self.max_length}


class StrippedVARCHAR(VARCHAR):
    def clean(self, value):
        value = super(StrippedVARCHAR, self).clean(value)
        return value.strip()


class IPAddress(Field):
    def __init__(self, ip_type=None, **kwargs):
        self.ip_type = ip_type
        super(IPAddress, self).__init__(**kwargs)

    def clean(self, value):
        if self.ip_type is None:
            return ipaddr.IPAddress(value)
        elif self.ip_type == 4:
            return ipaddr.IPv4Address(value)
        elif self.ip_type == 6:
            return ipaddr.IPv6Address(value)
        else:
            raise Exception(u'Not implemented')

    def to_db(self, db, value):
        ip_int = int(self.value)
        return {
            u'upper': ip_int >> 64,
            u'lower': ip_int & (2**64 - 1)
        }

    def from_db(self, db, columns):
        return self.clean((columns[u'upper'] << 64) | columns[u'lower'])

    column_info = {
        u'mysql': (
            (u'upper', u'BIGINT UNSIGNED'),
            (u'lower', u'BIGINT UNSIGNED')
        )
    }
