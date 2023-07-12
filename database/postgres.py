from configuration.conf import Config
import psycopg2


class Database:
    @property
    def connection(self):
        cfg = Config()
        return psycopg2.connect(
            database=cfg.dbase,
            user=cfg.user,
            password=cfg.password,
            host=cfg.host,
            port='5432'
        )

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def check_auth(self, chat):
        sql = '''
            SELECT id, access FROM aida_users WHERE 
            chat = %s;
        '''
        params = (chat, )
        return self.execute(sql, parameters=params, fetchone=True)

    def add_stationary(self, unit):
        sql = '''
            INSERT INTO aida_stationary (name, uuid, rest_id, code, tz, user_id, subs) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        params = (unit['name'], unit['uuid'], unit['id'], unit['code'], unit['tz'], [unit['user_id']], unit['sub'])
        self.execute(sql, parameters=params, commit=True)

    def update_stationary(self, unit):
        sql = '''
            UPDATE aida_stationary
            SET user_id = user_id || %s, subs = %s
            WHERE NOT (user_id @> %s OR user_id = %s) AND uuid = %s;
        '''
        params = ([unit['user_id']], unit['sub'], [unit['user_id']], [unit['user_id']], unit['uuid'])
        self.execute(sql, parameters=params, commit=True)

    def check_stationary(self, uuid):
        sql = '''
            SELECT EXISTS (SELECT 1 FROM aida_stationary WHERE uuid = %s);
        '''
        params = (uuid,)
        return self.execute(sql, parameters=params, fetchone=True)
