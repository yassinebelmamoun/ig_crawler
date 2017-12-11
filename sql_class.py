import sqlalchemy
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.exc import InvalidRequestError

from config import config


class Sql(object):

    def __init__(self, user, password, database, host='localhost', port=5432):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port

        connection, metadata = self.connect()
        self.connection = connection
        self.metadata = metadata

        self.table = self.create_users_table()

    def connect(self):
        # Returns a connection and a metadata object
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(self.user, self.password, self.host, self.port, self.database)

        # The return value of create_engine() is our connection object
        connection = sqlalchemy.create_engine(url, client_encoding='utf8')

        # We then bind the connection to MetaData()
        metadata = sqlalchemy.MetaData(bind=connection, reflect=True)

        return connection, metadata

    def create_users_table(self):
        try:
            users = Table(
                config.get('postgres_table'), self.metadata,
                Column('id', Integer, primary_key=True),
                Column('user_id', String),
                Column('from_user_id', String),
                Column('username', String),
                Column('full_name', String),
                Column('is_private', String),
                Column('media_count', Integer),
                Column('profile_pic_url', String),
                Column('follower_count', Integer),
                Column('following_count', Integer),
                Column('biography', String),
                Column('usertags_count', Integer),
                )

            # Create the above table
            self.metadata.create_all(self.connection)
            print('Table users is created')
            return users
        except InvalidRequestError:
            print('Table users was already created')
            users = self.metadata.tables[config.get('postgres_table')]
            return users

    def insert_user_in_table(self, user_dict):
        clause = self.table.insert().values(**user_dict)
        result = self.connection.execute(clause)
        pk = result.inserted_primary_key
        print('Inserted user ', pk)
        return pk

    def is_user_id_in_table(self, user_id):
        clause = self.table.select().where(self.table.c.user_id == user_id)
        result = self.connection.execute(clause)
        for _ in result:
            print('User {} already in db'.format(user_id))
            return True
        return False


if __name__ == '__main__':
    sql = Sql(
        user=config.get('postgres_user'),
        password=config.get('postgres_password'),
        database=config.get('postgres_database'),
    )
    test_user = {'user_id': '4172793932', 'from_user_id': None, 'username': 'thisisjaney', 'full_name': '✨FB : Tidakan kawipongbunsiri', 'is_private': False, 'media_count': 152, 'profile_pic_url': 'https://scontent-cdg2-1.cdninstagram.com/t51.2885-19/s150x150/24274562_2084892915076925_8415373467389526016_n.jpg', 'follower_count': 36694, 'following_count': 237, 'biography': '✨Work Line : @tcg_group/direct', 'usertags_count': 38}
    sql.insert_user_in_table(test_user)
    sql.is_user_id_in_table('4172793932')
    sql.is_user_id_in_table('4172793132')
