from peewee import SqliteDatabase, Model
from playhouse.migrate import migrate, SqliteMigrator
from peewee import IntegerField, CharField, TextField, ForeignKeyField, BitField, DateTimeField
from peewee import OperationalError
import datetime


database = SqliteDatabase("bot.db")
migrator = SqliteMigrator(database)


class BaseModel(Model):
    class Meta:
        database = database


class Users(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField(max_length=300, null=True)
    mega_username = CharField(max_length=300, null=True)
    maga_password = CharField(max_length=300, null=True)

    @classmethod
    def add_user(cls, user_id, username):
        q = cls.insert(user_id=user_id, username=username).on_conflict_ignore(ignore=True)
        q.execute()

    @classmethod
    def add_mega_info(cls, mega_username,  maga_password, user_id):
        data = {'mega_username': mega_username, 'maga_password': maga_password}
        cls.update(data).where(Users.user_id == user_id).execute()

    @classmethod
    def get_mega_info(cls, user_id):
        user = cls.get(cls.user_id == user_id)
        return user

    @classmethod
    def admins(cls):
        t = cls.select(Users.user_id).where(Users.is_admin == 1).tuples()
        users = []
        for user_id in t:
            users.append(user_id[0])
        return users


class Admins(BaseModel):
    admin_id = ForeignKeyField(Users)

    @classmethod
    def add_admin(cls, admin_id):
        q = cls.insert(admin_id=admin_id).on_conflict_ignore(ignore=True)
        q.execute()


class Files(BaseModel):
    file_id = TextField()
    user_id = ForeignKeyField(Users)
    uploaded = BitField(default=0)
    file_type = CharField(max_length=15)
    datetime_upload = DateTimeField(default=datetime.datetime.now(), formats="%Y-%m-%d %H:%M:%S")
    file_code = CharField(max_length=10, null=True)

    @classmethod
    def add_file(cls, file_id, user_id, file_type, file_code):
        cls.create(file_id=file_id, user_id=user_id, file_type=file_type, file_code=file_code)

    @classmethod
    def add_upload_status(cls, uploaded, file_id):
        data = {'uploaded': 1}
        cls.update(data).where(cls.file_id == file_id).execute()

# updates on database


updates = [
    ('files', 'datetime_upload', Files.datetime_upload),
    ('files', 'file_code', Files.file_code),
]

for update in updates:
    try:
        migrate(migrator.add_column(*update))
    except OperationalError:
        pass






