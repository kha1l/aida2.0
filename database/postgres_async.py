import asyncpg
from configuration.conf import Config


class AsyncDatabase:
    def __init__(self):
        self.config = Config()
        self.dsn = f"postgresql://{self.config.user}:{self.config.password}@{self.config.host}:5432/{self.config.dbase}"

    async def create_pool(self):
        return await asyncpg.create_pool(dsn=self.dsn)

    @staticmethod
    async def execute(pool, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()

        async with pool.acquire() as connection:
            data = None
            async with connection.transaction():
                if fetchone:
                    data = await connection.fetchrow(sql, *parameters)
                elif fetchall:
                    data = await connection.fetch(sql, *parameters)
                else:
                    await connection.execute(sql, *parameters)

        return data

    async def add_user(self, pool, user_id, username, name, sub):
        sql = '''
            INSERT INTO aida_users (user_id, username, name, sub) VALUES 
            ($1, $2, $3, $4) RETURNING id
        '''
        params = (user_id, username, name, sub)
        return await self.execute(pool, sql, parameters=params, commit=True, fetchone=True)

    async def add_person(self, pool, id, person):
        sql = '''
            INSERT INTO aida_persons (user_id, name, email, phone, given_name,
            middle_name, family_name, concept, country) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        '''
        params = (id, person.name, person.email, person.phone, person.given_name,
                  person.middle_name, person.family_name, person.concept, person.country)
        await self.execute(pool, sql, parameters=params, commit=True)

    async def add_tokens(self, pool, id, access, refresh):
        sql = '''
            INSERT INTO aida_tokens (user_id, access, refresh) VALUES ($1, $2, $3)
        '''
        params = (id, access, refresh)
        await self.execute(pool, sql, parameters=params, commit=True)

    async def check_auth(self, pool, user_id):
        sql = '''
            SELECT id FROM aida_users WHERE
            user_id = $1;
        '''
        params = (user_id,)
        return await self.execute(pool, sql, parameters=params, fetchone=True)

    async def get_tokens(self, pool, id):
        sql = '''
            SELECT id, access, refresh FROM aida_tokens WHERE user_id = $1
        '''
        params = (id,)
        return await self.execute(pool, sql, parameters=params, fetchone=True)

    async def update_tokens(self, pool, id, access, refresh):
        sql = '''
            UPDATE aida_tokens SET access = $1, refresh = $2 WHERE user_id = $3
        '''
        params = (access, refresh, id)
        await self.execute(pool, sql, parameters=params, commit=True)

    async def add_stationary(self, pool, unit):
        sql = '''
            INSERT INTO aida_stationary (name, uuid, unit_id, country_code, timezone, user_id, subs, expires)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        '''
        params = (unit['name'], unit['uuid'], unit['id'], unit['code'], unit['tz'], [unit['user_id']],
                  unit['subs'], unit['expires'])
        await self.execute(pool, sql, parameters=params, commit=True)

    async def check_stationary(self, pool, uuid):
        sql = '''
            SELECT * FROM aida_stationary WHERE uuid = $1;
        '''
        params = (uuid,)
        return await self.execute(pool, sql, parameters=params, fetchone=True)

    async def update_stationary(self, pool, unit):
        sql = '''
            UPDATE aida_stationary
            SET 
                user_id = array_append(user_id, $2),
                subs = $3, expires = $4
            WHERE
                uuid = $1;
        '''
        params = (unit['uuid'], unit['user_id'], unit['subs'], unit['expires'])
        await self.execute(pool, sql, parameters=params, commit=True)

    async def update_stationary_sub_and_expires(self, pool, unit):
        sql = '''
            UPDATE aida_stationary
            SET subs = $2, expires = $3
            WHERE uuid = $1;
        '''
        params = (unit['uuid'], unit['subs'], unit['expires'])
        await self.execute(pool, sql, parameters=params, commit=True)

    async def select_stationary(self, pool, id):
        sql = '''
            SELECT name, unit_id, uuid, country_code, timezone, subs, expires
            FROM aida_stationary
            WHERE $1 = ANY(user_id);
        '''
        params = (id,)
        return await self.execute(pool, sql, parameters=params, fetchall=True)

    async def get_subs_id(self, pool):
        sql = '''
            SELECT id, name, function FROM aida_subs;
        '''
        return await self.execute(pool, sql, fetchall=True)

    async def get_functions(self, pool, call):
        sql = '''
            SELECT name, alias FROM aida_functions WHERE groups = $1
        '''
        params = (call, )
        return await self.execute(pool, sql, parameters=params, fetchall=True)

    async def get_func(self, pool, group):
        sql = '''
            SELECT name, alias FROM aida_stops WHERE groups = $1
        '''
        params = (group,)
        return await self.execute(pool, sql, parameters=params, fetchall=True)

    async def get_orders(self, pool, chat, post, country, tz):
        sql = '''
            SELECT id, uuid FROM aida_orders WHERE chat_id = $1 and post = $2 
            and country = $3 and timezone = $4
        '''
        params = (chat, post, country, tz)
        return await self.execute(pool, sql, parameters=params, fetchone=True)

    async def add_order(self, pool, post, uuid, user, chat, country, tz):
        sql = '''
            INSERT INTO aida_orders (post, uuid, user_id, chat_id, country, timezone) 
            VALUES ($1, $2, $3, $4, $5, $6)
        '''
        params = (post, uuid, user, chat, country, tz)
        await self.execute(pool, sql, parameters=params, commit=True)

    async def update_order(self, pool, uuid, id):
        sql = '''
            UPDATE aida_orders SET uuid = $1 WHERE id = $2
        '''
        params = (uuid, id)
        await self.execute(pool, sql, parameters=params, commit=True)

    async def drop_order(self, pool, id):
        sql = '''
            DELETE FROM aida_orders WHERE id = $1
        '''
        params = (id, )
        await self.execute(pool, sql, parameters=params, commit=True)
