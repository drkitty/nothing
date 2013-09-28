from types import FunctionType

class Field(object):
    def __new__(cls, *args, **kwargs):
        @staticmethod
        def _create_field():
            obj = super(Field, cls).__new__(cls)
            obj.__init__(*args, **kwargs)
            return obj

        return _create_field

    def __init__(self):
        self.value = None

    def clean(self, value):
        return value

    def to_db(self, db_type):
        return self.value

    def from_db(self, db_type, value):
        return value

    def __unicode__(self):
        return unicode(self.value)


class Model(object):
    def __init__(self, pk=None, **field_values):
        #if pk is not None:
            #field_values = self.objects.get(pk=pk)
        for fieldname, value in field_values.iteritems():
            getattr(self, fieldname).value = value

        for name in dir(self):
            attr = getattr(self, name)
            if (isinstance(attr, FunctionType) and
                    attr.__name__ == '_create_field'):
                setattr(self, name, attr())

    def __getattribute__(self, name):
        attr = super(Model, self).__getattribute__(name)
        if isinstance(attr, Field):
            return attr.value
        else:
            return attr

    def __setattr__(self, name, value):
        attr = super(Model, self).__getattribute__(name)
        if isinstance(attr, Field):
            super(Model, self).__setattr__(name, attr.clean(value))
        else:
            super(Model, self).__setattr__(name, value)
