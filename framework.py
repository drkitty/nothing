class Field(object):
    def __new__(cls, *args, **kwargs):
        @staticmethod
        def new():
            obj = super(Field, cls).__new__(cls)
            obj.__init__(*args, **kwargs)
            return obj

        return new

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


def build_model(name, bases, attrs):
    model = type(name, bases, {})
    model._fields = type('_fields', (object,), {})

    fieldnames = set()
    for attrname, value in attrs.iteritems():
        print 'Handling {0}: {1}'.format(attrname, value)
        if isinstance(value, staticmethod):
            print 'Adding {0} to model._fields'.format(attrname)
            setattr(model._fields, attrname, value)
            fieldnames.add(attrname)
        else:
            print 'Adding {0} to model'.format(attrname)
            setattr(model, attrname, value)
    model._fields._names = fieldnames

    def ga(self, name):
        if hasattr(self._fields, name):
            return getattr(self._fields, name).value
        else:
            raise AttributeError()

    def sa(self, name, value):
        if hasattr(self._fields, name):
            field = getattr(self._fields, name)
            field.value = field.clean(value)
        else:
            raise AttributeError()

    model.__getattr__ = ga
    model.__setattr__ = sa

    return model


class Model(object):
    def __init__(self, pk=None, **field_values):
        #if pk is not None:
            #field_values = self.objects.get(pk=pk)
        for fieldname, value in field_values.iteritems():
            getattr(self._fields, fieldname).value = value

        for fieldname in self._fields._names:
            setattr(self._fields, fieldname,
                    getattr(self._fields, fieldname)())
