from types import FunctionType


class Database(object):
    pass


class MySQLDatabase(Database):
    db_type = u'mysql'

    def __init__(self, host, user, passwd, db):
        import oursql
        self.connection = oursql.Connection(host, user, passwd, db=db)
        self.cursor = self.connection.cursor()

    def create_table(self, table_name, columns):
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
        column_info = self._column_info[db.db_type]
        if isinstance(column_info, tuple):
            columns = []
            for (column_suffix, column_type) in column_info:
                columns.append((self.column_name + u'_' + column_suffix,
                                column_type))
        else:
            column_type = column_info
            columns = [(self.column_name, column_type)]

        return columns

    _column_info = ()


class Model(object):
    def __init__(self, pk=None, **field_values):
        super(Model, self).__setattr__(u'_fields', [])

        #if pk is not None:
            #field_values = self.objects.get(pk=pk)
        for fieldname, value in field_values.iteritems():
            getattr(self, fieldname).value = value

        for attrname in dir(self):
            attr = getattr(self, attrname)
            if (isinstance(attr, FunctionType) and
                    attr.__name__ == '_create_field'):
                # Why is it a function now, when it used to be a staticmethod?
                # Something to do with class instantiation.
                setattr(self, attrname, attr(attrname))
                self._fields.append(attrname)

        self._fields = tuple(self._fields)

    def __getattribute__(self, name):
        attr = super(Model, self).__getattribute__(name)
        if isinstance(attr, Field):
            return attr.value
        else:
            return attr

    def __setattr__(self, name, value):
        try:
            attr = super(Model, self).__getattribute__(name)
        except AttributeError:
            super(Model, self).__setattr__(name, value)
            return

        if isinstance(attr, Field):
            attr.value = attr.clean(value)
        else:
            super(Model, self).__setattr__(name, value)

    def _create_table(self, db):
        columns = []
        for fieldname in self._fields:
            field = super(Model, self).__getattribute__(fieldname)
            columns += field.create_columns(db)


        try: # can't use hasattr because we defined __getattribute__
            table_name = self._table_name
        except AttributeError:
            table_name = self.__class__.__name__.lower()

        return db.create_table(table_name, columns)

    def _drop_table(self, db):
        return db.drop_table(table_name)
