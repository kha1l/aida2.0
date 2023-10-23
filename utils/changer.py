from loggs.logger import Log
from database.postgres_async import AsyncDatabase


async def change_orders():
    logger = Log('CHANGE_ORDERS')
    db = AsyncDatabase()
    pool = await db.create_pool()
    orders = await db.select_all_orders(pool)
    units = await db.select_all_stationary(pool)
    units_sub = {}
    for unit in units:
        units_sub[unit['uuid']] = unit['subs']
    for order in orders:
        uuids = order['uuid']
        for uuid in uuids:
            pass
    await pool.close()