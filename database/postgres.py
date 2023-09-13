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

    def add_user(self, user_id, username, name, sub):
        sql = '''
            INSERT INTO aida_users (user_id, username, name, sub) VALUES 
            (%s, %s, %s, %s) RETURNING id
        '''
        params = (user_id, username, name, sub)
        return self.execute(sql, parameters=params, commit=True, fetchone=True)

    def add_person(self, id, person):
        sql = '''
            INSERT INTO aida_persons (user_id, name, email, phone, given_name,
            middle_name, family_name, concept, country) VALUES (%s, %s, %s, %s, %s, 
            %s, %s, %s, %s)
        '''
        params = (id, person.name, person.email, person.phone, person.given_name,
                  person.middle_name, person.family_name, person.concept, person.country)
        self.execute(sql, parameters=params, commit=True)

    def add_tokens(self, id, access, refresh):
        sql = '''
            INSERT INTO aida_tokens (user_id, access, refresh) VALUES (%s, %s, %s)
        '''
        params = (id, access, refresh)
        self.execute(sql, parameters=params, commit=True)

    def check_auth(self, user_id, sub):
        sql = '''
            SELECT id FROM aida_users WHERE
            user_id = %s AND sub = %s;
        '''
        params = (user_id, sub)
        return self.execute(sql, parameters=params, fetchone=True)

    def check_auth_id(self, user_id):
        sql = '''
            SELECT id FROM aida_users WHERE
            user_id = %s;
        '''
        params = (user_id,)
        return self.execute(sql, parameters=params, fetchall=True)

    def get_tokens(self, id):
        sql = '''
            SELECT id, access, refresh FROM aida_tokens WHERE user_id = %s
        '''
        params = (id, )
        return self.execute(sql, parameters=params, fetchone=True)

    def add_stationary(self, unit):
        sql = '''
            INSERT INTO aida_stationary (name, uuid, unit_id, country_code, timezone, user_id, subs, expires)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        params = (unit['name'], unit['uuid'], unit['id'], unit['code'], unit['tz'], [unit['user_id']],
                  unit['sub'], unit['expires'])
        self.execute(sql, parameters=params, commit=True)

    def update_stationary(self, unit):
        sql = '''
            UPDATE aida_stationary
            SET user_id = user_id || %s, subs = %s, expires = %s
            WHERE NOT (user_id @> %s OR user_id = %s) AND uuid = %s;
        '''
        params = ([unit['user_id']], unit['subs'], unit['expires'], [unit['user_id']],
                  [unit['user_id']], unit['uuid'])
        self.execute(sql, parameters=params, commit=True)

    def check_stationary(self, uuid):
        sql = '''
            SELECT EXISTS (SELECT 1 FROM aida_stationary WHERE uuid = %s);
        '''
        params = (uuid,)
        return self.execute(sql, parameters=params, fetchone=True)
