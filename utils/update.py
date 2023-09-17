from database.postgres_async import AsyncDatabase
from loggs.logger import Log
from utils.connection import Connect
from .stationary import add_stationary


async def update_subs(**kwargs):
    upd_units, add_units = [], []
    try:
        db = AsyncDatabase()
        pool = await db.create_pool()
        tokens = await db.get_tokens(pool, kwargs['id'])
        access_units, subs = await add_stationary(kwargs['id'], tokens['access'])
        for units in access_units:
            reach = await db.check_stationary(pool, units['uuid'])
            if reach:
                if units['user_id'] not in reach['user_id']:
                    await db.update_stationary(pool, units)
                else:
                    if reach['expires'] != units['expires'] \
                            or reach['subs'] != units['subs']:
                        upd_units.append(units['name'])
                        await db.update_stationary_sub_and_expires(pool, units)
            else:
                add_units.append(units['name'])
                await db.add_stationary(pool, units)
        await pool.close()
        return add_units, upd_units
    except KeyError:
        return [], []


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


async def update_subs_day():
    logger = Log('UPDATE SUBS')
    db = AsyncDatabase()
    pool = await db.create_pool()
    units = await db.get_stationary(pool)
    for unit in units:
        tokens = await db.get_tokens(pool, unit['unit_id'][0])
    await pool.close()
