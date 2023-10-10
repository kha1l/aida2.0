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
                    try:
                        delta_value = value / avg_value
                    except ZeroDivisionError:
                        delta_value = 0
                    if 0.667 < delta_value <= 1:
                        step = f'3 дня \U000026A0'
                    elif 0.334 < delta_value <= 0.667:
                        step = f'2 дня \U00002757'
                    elif delta_value <= 0.334:
                        step = f'1 день \U0000203C'
                    else:
                        step = f'не осталось в запасах'
                    if step == 'не осталось в запасах':
                        if unit != unit_prev:
                            message += f'<b>{unit}</b>\n'
                        message += f'<b>{unit}:</b>\n<b>{item_name} {step}</b> \U0001F198\n'
                        unit_prev = unit
                    else:
                        if meas == 'шт':
                            value = int(value)
                        else:
                            value = round(value, 2)
                        if unit != unit_prev:
                            message += f'<b>{unit}:</b>\n'
                        message += f'<b>{item_name}</b>\n' \
                                   f'осталось {value} {meas}\n' \
                                   f'по прогнозу хватит на {step}\n\n'
                        unit_prev = unit
        if message != '\U0001F9C0 Складские остатки на {dt_day}:\n\n':
            await send.sending(order["chat_id"], message, logger, order['id'])
    await pool.close()
