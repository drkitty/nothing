from types import FunctionType


class Database(object):
    pass


class MySQLDatabase(Database):
    db_type = u'mysql'

    def __init__(self, host, user, passwd, db):
        import oursql
        self.connection = oursql.Connection(host, user, passwd, db=db)
        self.cursor = self.connection.cursor()
        self.execute = self.cursor.execute

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.connection.close()

    def _create_table(self, table_name, columns):
        sql = (u'CREATE TABLE %s\n'
               u'(\n'
               % table_name)

        for i in xrange(len(columns)):
            sql += u'%s %s' % (columns[i][0], columns[i][1])
            if i != len(columns) - 1:
                sql += u',\n'
            else:
                sql += u'\n'

        sql += u');\n'

        return sql

class Field(object):
    """The base field class
    Fields are like columns except when they're like groups of columns.
    """

    def __new__(cls, *args, **kwargs):
        @staticmethod
        def _create_field(column_name):
            kwargs['column_name'] = column_name
            obj = super(Field, cls).__new__(cls)
            obj.__init__(*args, **kwargs)
            return obj

        return _create_field

    def __init__(self, column_name=None, default=None):
        self.value = default
        if column_name:
            self.column_name = unicode(column_name)
        else:
            raise Exception('No column name given')

    def clean(self, value):
        return value

    def to_db(self, db):
        return self.value

    def from_db(self, db, value):
        return value

    def __unicode__(self):
        return unicode(self.value)

    def create_columns(self, db):
        column_info = self.column_info[db.db_type]
        if isinstance(column_info, tuple):
            columns = []
            for (column_suffix, column_type) in column_info:
                columns.append((self.column_name + u'_' + column_suffix,
                                column_type))
        else:
            column_type = column_info
            columns = [(self.column_name, column_type)]

        return columns

    column_info = ()


class Model(object):
    """The base model class
    Models are like tables.

    Note: Attributes that are not Field instances should begin with an
    underscore (because of reasons).
    """

    @classmethod
    def _get_fields(cls):
        fields = {}

        for attrname in dir(cls):
            attr = getattr(cls, attrname)
            if (isinstance(attr, FunctionType) and
                    attr.__name__ == '_create_field'):
                # Why is it a function now, when it used to be a staticmethod?
                # Something to do with class instantiation.
                fields[attrname] = attr(attrname)

        return fields

    def __init__(self):
        super(Model, self).__setattr__('_fields', {})

        # ^^ def __init__(..., pk=None, ...):
        #if pk is not None:
            #db_values = self.objects.get(pk=pk)
            #for fieldname, value in db_values.iteritems():
                #getattr(self, fieldname).value = value

        for attrname in dir(self):
            attr = getattr(self, attrname)
            if (isinstance(attr, FunctionType) and
                    attr.__name__ == '_create_field'):
                # Why is it a function now, when it used to be a staticmethod?
                # Something to do with class instantiation.
                attr = attr(attrname)
                setattr(self, attrname, attr)
                self._fields[attrname] = attr

    def __getattribute__(self, name):
        attr = super(Model, self).__getattribute__(name)
        if name == '_fields' or name not in self._fields.iterkeys():
            return attr
        else:
            return attr.value

    def __setattr__(self, name, value):
        if name in self._fields:
            attr= super(Model, self).__getattribute__(name)
            attr.value = attr.clean(value)
        else:
            super(Model, self).__setattr__(name, value)

    @classmethod
    def _create_table(cls, db):
        columns = []
        fields = cls._get_fields()
        for field in fields.itervalues():
            columns += field.create_columns(db)

        try: # can't use hasattr because we defined __getattribute__
            table_name = cls._table_name
        except AttributeError:
            table_name = cls.__name__.lower()

        return db._create_table(table_name, columns)

    def _drop_table(self, db):
        return db.drop_table(table_name)
