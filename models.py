from framework import Field, Model

class StrippedCharField(Field):
    def __init__(self):
        self.value = u''

    def clean(self, value):
        return unicode(value.strip())


class Thing(Model):
    foo = StrippedCharField()
