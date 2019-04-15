'''
 v5
- select->filter
- переделан where
'''

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


class Field(object):
    def __init__(self, f_type):
        self.f_type = f_type

    def validate(self, value):
        if value is None:
            return None
        if type(value) == self.f_type:
            return self.f_type(value)
        else:
            raise Exception


class INTEGER(Field):
    def __init__(self):
        super(INTEGER, self).__init__(int)


class TEXT(Field):
    def __init__(self):
        super(TEXT, self).__init__(str)


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            return super().__new__(mcs, name, bases, attrs)
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        bases_fields = {}
        for base in bases:
            if base.__name__ != 'Model':
                bases_fields.update(base.__dict__.get('_fields'))
        bases_fields.update(fields)
        attrs['_fields'] = bases_fields
        return super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)


class Manager(object):
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if instance:
            raise Exception
        if self.model_cls is None:
            self.model_cls = owner
        return self

    def filter(self, *args, limit=None, **kwargs):
        '''Выборка из базы данных'''

        def transform(cls):
            result = cursor.fetchall()
            attrs = [i for i in cls.__dict__.keys() if i[:1] != '_']
            for index, obj in enumerate(result):
                model = cls()
                for index1, attr in enumerate(attrs):
                    setattr(model, attr, obj[index1])
                result[index] = model
            if not result:
                raise Exception("{}.DoesNotExist".format(cls.__name__))
            return result

        clas = self.model_cls

        if args == '*':
            sql = args
        else:
            sql = ",".join(["{}".format(column) for column in args])

        replacement_dict = {'lt': '<', 'le': '<=', 'eq': '=', 'ne': '!=', 'gt': '>', 'ge': '>=', 'is': 'is'}
        if not kwargs:
            where = None

        where = list(kwargs.items())
        where_col = [i[0].split('__')[0] for i in where]
        where_operation = [i[0].split('__')[1] for i in where]
        where_val = [i[1] for i in where]
        where_operation = list(map(lambda i: replacement_dict.get(i), where_operation))
        if None in where_operation:
            raise Exception('incorrect operation in where statement')

        if not where and not limit:
            cursor.execute("SELECT {} FROM {}".format(sql, clas.__name__))
            return transform(clas)
        if where and not limit:
            where_str = ' AND '.join([where_col[i] + where_operation[i] + '?' for i in range(len(where))])
            cursor.execute(
                "SELECT {} FROM {} WHERE {}".format(sql, clas.__name__, where_str),
                where_val)
            return transform(clas)
        if not where and limit:
            cursor.execute("SELECT {} FROM {} LIMIT {}".format(sql, clas.__name__, limit))
            return transform(clas)
        if where and limit:
            where_str = ' AND '.join([where_col[i] + where_operation[i] + '?' for i in range(len(where))])
            cursor.execute(
                "SELECT {} FROM {} WHERE {} LIMIT {}".format(sql, clas.__name__, where_str,
                                                             limit),
                where_val)
            return transform(clas)


class Model(metaclass=ModelMeta):
    objects = Manager()

    def __init__(self, *_, **kwargs):
        for field_name, field_value in self.__class__.__dict__.get("_fields").items():
            value = field_value.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

    def add(self, table_name=None):
        '''Добавление значения в таблицу'''
        if not table_name:
            table_name = self.__class__.__name__
        cursor.execute("pragma table_info({})".format(table_name))
        info = cursor.fetchall()
        if not info:
            parameters = ",".join(["{} {}".format(k, getattr(self.__class__, k).__class__.__name__)
                                   for k in self.__class__.__dict__.get("__fields").keys()])
            cursor.execute("CREATE TABLE {}({})".format(table_name, parameters))
        columns = ",".join(["{}".format(k)
                            for k, v in self.__dict__.items() if v != None])
        value = tuple(["{}".format(v) if type(v) == int else "'{}'".format(v)
                       for v in self.__dict__.values() if v != None])
        cursor.execute("INSERT INTO {}({}) VALUES ({})".format(table_name, columns, ('?,' * len(value))[:-1]), value)
        # Result: INSERT INTO User(id,age) VALUES (?,?) <- value
        conn.commit()

    def remove(self, table_name=None):
        '''Добавление значения из таблицы'''
        if not table_name:
            table_name = self.__class__.__name__
        sql = " AND ".join(["{}={}".format(k, v) if type(v) == int else "{}='{}'".format(k, v)
                            for k, v in self.__dict__.items() if v != None])
        try:
            pass
            cursor.execute("DELETE FROM {} WHERE {}".format(table_name, sql))
            conn.commit()
        except:
            print('Данного значения не существует, удалять нечего')


def create_model(table_name):
    '''Создание представления в виде класса по таблице в БД'''
    cursor.execute("pragma table_info({})".format(table_name))
    columns = cursor.fetchall()
    attrs = dict([(i[1], INTEGER()) if i[2] == 'INTEGER' else (i[1], TEXT()) for i in columns])
    return type(table_name, (Model,), attrs)


class User(Model):
    id = INTEGER()
    name = TEXT()
    age = INTEGER()


# class Student(User):
#     age = TEXT()

# User.objects.filter('*', id__gt=10)
# User(name='Ivan',id=2).add()
# users = User.objects.filter('*', id__gt=1, age__gt=3)
# for i in users:
#     print(i.age)
# for user in users:
#     print(user.id)
# Book = create_model("Book")
# user = User(id=10, age=20)
# user.add()
# Book.objects.select('*')
cursor.close()
