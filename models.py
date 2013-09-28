from framework import Field, Model, build_model

class StrippedCharField(Field):
    def __init__(self):
        self.value = u''

    def clean(self, value):
        return unicode(value.strip())


class Thing(Model):
    __metaclass__ = build_model

    foo = StrippedCharField()
