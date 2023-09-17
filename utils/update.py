from database.postgres_async import AsyncDatabase
from authorization.users import DataUser
from loggs.logger import Log
from utils.connection import Connect


async def update_subs(**kwargs):
    try:
        db = AsyncDatabase()
        pool = await db.create_pool()
        tokens = await db.get_tokens(pool, kwargs['id'])
        user = DataUser(tokens['access'])
        units = await user.get_subs()
        print(units)
        print(kwargs['units'])
        await pool.close()
    except KeyError:
        return []


async def update_tokens_app():
    logger = Log('UPDATE APP')
    db = AsyncDatabase()
    pool = await db.create_pool()
    tokens = await db.select_tokens(pool)
    link = 'https://auth.dodois.io/connect/token'
    conn = Connect()
    for token in tokens:
        token_response = await conn.update_tokens(url=link, refresh=token['refresh'])
        try:
            access = token_response['access_token']
            refresh = token_response['refresh_token']
            await db.update_tokens(pool, token['id'], access, refresh)
            logger.info(f'UPDATE TOKEN {token["id"]} - OK')
        except KeyError:
            logger.error(f'Key ERROR update_app - {token["id"]}')
        except TypeError:
            logger.error(f'Type ERROR update_app - {token["id"]}')
    await pool.close()

