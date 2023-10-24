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
        add_uuids = []
        for uuid in uuids:
            value = units_sub.get(uuid)
            if value:
                if value == 'premium':
                    add_uuids.append(uuid)
        if uuids != add_uuids:
            if add_uuids:
                await db.update_order_with_subs(pool, order['id'], add_uuids)
                logger.info(f'UPDATE order id = {order["id"]} on user_id = {order["user_id"]}')
            else:
                await db.drop_order(pool, order['id'])
                logger.info(f'DROP order id = {order["id"]} on user_id = {order["user_id"]}')
    await pool.close()
