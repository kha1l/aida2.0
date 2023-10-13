from database.postgres_async import AsyncDatabase
from utils.sending import Send
from loggs.logger import Log
from datetime import date


async def send_stock():
    db = AsyncDatabase()
    pool = await db.create_pool()
    send = Send(db=db)
    logger = Log('stock')
    orders = await db.select_orders(pool, 'stock')
    mess = f'\U0001F4D6 Напоминание\n\n' \
           f'Прошло 7 дней с момента внесения файла с ревизией. Если за это время была еще ревизия, ' \
           f'обновите файл с актуальными данными по ревизии в ресторане! \U0001F4D6'
    for order in orders:
        items = await db.select_items(pool, order['uuid'])
        unit_prev = ''
        dt_now = date.today()
        try:
            dt = (items[0]['date_audit']).date()
        except IndexError:
            dt = None
        if dt:
            day = (dt_now - dt).days
            if day % 7 == 0:
                await send.sending(order["chat_id"], mess, logger, order['id'])
        for item in items:
            value = item['quantity']
            avg_value = item['avgconsum']
            item_name = item['name']
            unit = item['unit']
            meas = item['measurement']
            message = f'\U0001F9C0 Складские остатки в {unit}:\n\n'
            if avg_value:
                if value * 2 <= avg_value:
                    if unit != unit_prev:
                        message += f'<b>{unit}</b>\n'
                    message += f'<b>{item_name}</b> заканчивается запас \U000026A0\n'
                    unit_prev = unit
                    if meas == 'шт':
                        value = int(value)
                    else:
                        value = round(value, 2)
                    message += f'осталось {value} {meas}\n'
                    if value < 0:
                        message += f'(проверьте внесен ли приход или корректные ли замеры)\n'
                    message += f'на 2 дня необходимо {avg_value} {meas}\n\n'
            if message != f'\U0001F9C0 Складские остатки в {unit}:\n\n':
                await send.sending(order["chat_id"], message, logger, order['id'])
    await pool.close()
