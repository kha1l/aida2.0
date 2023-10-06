from database.postgres_async import AsyncDatabase
from loggs.logger import Log
from utils.connection import Connect
from .stationary import add_stationary
from datetime import datetime, timedelta
from authorization.users import DataUser


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
                minutes = reach['timezone'] * 60 - 180
                dt = ((datetime.now().replace(minute=0, second=0, microsecond=0)) + timedelta(
                    minutes=minutes)).date()
                dt = datetime.strftime(dt, '%Y-%m-%d')
                if units['user_id'] not in reach['user_id']:
                    await db.update_stationary(pool, units)
                else:
                    if reach['expires'] != units['expires'] \
                            or reach['subs'] != units['subs']:
                        upd_units.append(units['name'])
                        await db.update_stationary_sub_and_expires(pool, units, reach['id'], dt)
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
        except Exception as e:
            logger.error(f'ERROR update_app - {token["id"]} - {e}')
            await db.delete_user(pool, token['id'])
    await pool.close()


async def update_subs_day():
    logger = Log('UPDATE SUBS')
    db = AsyncDatabase()
    pool = await db.create_pool()
    units = await db.get_stationary(pool)
    date_update = datetime.now().date()
    dt = datetime.strftime(date_update, '%Y-%m-%d')
    for unit in units:
        step = 0
        tokens = None
        data = {}
        if dt != unit['date_update']:
            while not tokens:
                try:
                    tokens = await db.get_tokens(pool, unit['user_id'][step])
                    if tokens:
                        user = DataUser(tokens["access"])
                        subs = await user.get_subs()
                        if unit['uuid'] in subs:
                            subscribe = subs[unit['uuid']][0]
                            expires = subs[unit['uuid']][1]
                        else:
                            subscribe = 'free'
                            expires = 'forever'
                        data['expires'] = expires
                        data['subs'] = subscribe
                        await db.update_stationary_sub_and_expires(pool, data, unit['id'], dt)
                    step += 1
                except IndexError:
                    logger.error(f'ERROR CANT UPDATE sub for unit {unit["id"]}')
                    break
    await pool.close()
