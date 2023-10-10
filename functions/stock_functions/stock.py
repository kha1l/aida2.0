from database.postgres_async import AsyncDatabase
from utils.sending import Send
from loggs.logger import Log
from datetime import datetime


async def send_stock():
    db = AsyncDatabase()
    pool = await db.create_pool()
    send = Send(db=db)
    logger = Log('stock')
    orders = await db.select_orders(pool, 'stock')
    dt = datetime.now().date()
    dt_day = datetime.strftime(dt, '%d.%m.%Y')
    for order in orders:
        items = await db.select_items(pool, order['uuid'])
        message = f'\U0001F9C0 Складские остатки на {dt_day}:\n\n'
        unit_prev = ''
        for item in items:
            value = item['quantity']
            avg_value = item['avgconsum']
            item_name = item['name']
            unit = item['unit']
            meas = item['measurement']
            if avg_value:
                if value <= avg_value:
                    if unit != unit_prev:
                        message += f'<b>{unit}</b>\n'
                    message += f'<b>{item_name}</b> заканчивается запас!! \U000026A0\n'
                    unit_prev = unit
                    if meas == 'шт':
                        value = int(value)
                    else:
                        value = round(value, 2)
                    message += f'осталось {value} {meas}\n'
                    if value < 0:
                        message += f'(проверьте внесен ли приход или корректные ли замеры)\n'
                    message += f'на 2 дня необходимо {avg_value} {meas}\n\n'
        if message != f'\U0001F9C0 Складские остатки на {dt_day}:\n\n':
            await send.sending(order["chat_id"], message, logger, order['id'])
    await pool.close()
